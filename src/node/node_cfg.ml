(*
This file is part of Arakoon, a distributed key-value store. Copyright
(C) 2010 Incubaid BVBA

Licensees holding a valid Incubaid license may use this file in
accordance with Incubaid's Arakoon commercial license agreement. For
more information on how to enter into this agreement, please contact
Incubaid (contact details can be found on www.arakoon.org/licensing).

Alternatively, this file may be redistributed and/or modified under
the terms of the GNU Affero General Public License version 3, as
published by the Free Software Foundation. Under this license, this
file is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.

See the GNU Affero General Public License for more details.
You should have received a copy of the
GNU Affero General Public License along with this program (file "COPYING").
If not, see <http://www.gnu.org/licenses/>.
*)

let config_file = ref "cfg/arakoon.ini"

let default_lease_period = 10

module Node_cfg = struct
  type t = {node_name:string;
	    ip:string;
	    client_port:int;
	    messaging_port:int;
	    home:string;
	    tlog_dir:string;
	    log_dir:string;
	    log_level:string;
	    lease_period:int;
	    forced_master: string option;
	   }

  type cluster_cfg = 
      { cfgs: t list;
	_forced_master: string option;
	quorum_function: int -> int;
	_lease_period: int;
	cluster_id : string;
      }

  let make_test_config n_nodes forced_master lease_period = 
    let make_one n =
      let ns = (string_of_int n) in
      let home = "#MEM#t_arakoon_" ^ ns in
      {
	node_name = "t_arakoon_" ^ ns;
	ip = "127.0.0.1";
	client_port = (4000 + n);
	messaging_port = (4010 + n);
	home = home;
	tlog_dir = home;
	log_dir = "none";
	log_level = "DEBUG";
	lease_period = lease_period;
	forced_master = forced_master;
      }
    in
    let rec loop acc = function
      | 0 -> acc
      | n -> let o = make_one (n-1) in
	     loop (o::acc) (n-1)
    in
    let cfgs = loop [] n_nodes in
    let quorum_function = Quorum.quorum_function in
    let lease_period = default_lease_period in
    let cluster_id = "ricky" in
    let cluster_cfg = { cfgs= cfgs; 
			_forced_master = forced_master;
			quorum_function = quorum_function;
			_lease_period = lease_period;
			cluster_id = cluster_id}
    in
    cluster_cfg
    

  let string_of (t:t) =
    let template =
      "{node_name=\"%s\"; ip=\"%s\"; client_port=%d; " ^^
	"messaging_port=%d; home=\"%s\"; tlog_dir=\"%s\"; log_dir=\"%s\"; log_level=\"%s\" }"
    in
      Printf.sprintf template
	t.node_name t.ip t.client_port t.messaging_port 
	t.home
	t.tlog_dir
	t.log_dir
	t.log_level

  let tlog_dir t = t.tlog_dir 
  let tlog_file_name t =
    t.home ^ "/" ^ t.node_name ^ ".tlog"

  let read_config config_file =
    let node_names inifile = 
      let nodes_s = inifile # getval "global" "nodes" in
      let nodes = Str.split (Str.regexp "[, \t]+") nodes_s in
      nodes
    in
    let lease_expiry inifile =
      try
	let les = (inifile # getval "global" "lease_expiry") in
	Scanf.sscanf les "%i" (fun i -> i)
      with (Inifiles.Invalid_element _) -> default_lease_period
    in
    let forced_master inifile =
      try
	let m = (inifile # getval "global" "master") in
	let nodes = node_names inifile in
	if not (List.mem m nodes)
	then
	  failwith (Printf.sprintf "'%s' needs to have a config section [%s]" m m)
        else Some m
      with (Inifiles.Invalid_element _) -> None
    in
    let get_cluster_id inifile =
      try
	let cids = inifile # getval "global" "cluster_id" in
	Scanf.sscanf cids "%s" (fun s -> s)
      with (Inifiles.Invalid_element _ ) -> failwith "config has no cluster_id"
    in
    let node_config inifile node_section fm =
      let get_string x =
	try
	  let strip s = Scanf.sscanf s "%s" (fun i -> i) in
	  let with_spaces= inifile # getval node_section x in
	  strip with_spaces
	with (Inifiles.Invalid_element e) ->
	  failwith (Printf.sprintf "'%s' was missing from %s"
		      e config_file)
      in
      let get_int x = Scanf.sscanf (get_string x) "%i" (fun i -> i) in

      let node_name = node_section in
      let ip = get_string "ip" in
      let client_port = get_int "client_port" in
      let messaging_port = get_int "messaging_port" in
      let home = get_string "home" in
      let tlog_dir = try get_string "tlog_dir" with _ -> home in
      let log_level = String.lowercase (get_string "log_level") in
      let lease_period = lease_expiry inifile in
      let log_dir = get_string "log_dir" in
	{node_name=node_name;
	 ip=ip;
	 client_port=client_port;
	 messaging_port= messaging_port;
	 home=home;
	 tlog_dir = tlog_dir;
	 log_dir = log_dir;
	 log_level = log_level;
	 lease_period = lease_period;
	 forced_master = fm;
	}
    in
    let inifile = new Inifiles.inifile config_file in
    let fm = forced_master inifile in
    let nodes = node_names inifile in
    let n_nodes = List.length nodes in
    let cfgs, remaining = List.fold_left
      (fun (a,remaining) section ->
	if List.mem section nodes
	then
	  let cfg = node_config inifile section fm in
	  let new_remaining = List.filter (fun x -> x <> section) remaining in
	  (cfg::a, new_remaining)
	else (a,remaining))
      ([],nodes) (inifile # sects) in
    let () = if List.length remaining > 0 then
	failwith ("Can't find config section for: " ^ (String.concat "," remaining))
    in
    
    
    let quorum_function =
      try
	let qs = (inifile # getval "global" "quorum") in
	let qi = Scanf.sscanf qs "%i" (fun i -> i) in
	if 1 <= qi & qi <= n_nodes then
	  fun n -> qi
	else
	  let msg = Printf.sprintf "fixed quorum should be 1 <= %i <= %i"
	    qi n_nodes in
	  failwith msg
      with (Inifiles.Invalid_element _) -> Quorum.quorum_function
    in
    let lease_period = lease_expiry inifile in
    let cluster_id = get_cluster_id inifile in
    let cluster_cfg = 
      { cfgs = cfgs;
	_forced_master = fm;
	quorum_function = quorum_function;
	_lease_period = lease_period;
	cluster_id = cluster_id}
    in
    cluster_cfg


  let node_name t = t.node_name
  let home t = t.home

  let client_address t = Network.make_address t.ip t.client_port
  
  let forced_master t = t.forced_master

  let get_node_cfgs_from_file () = read_config !config_file 

end
