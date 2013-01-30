open OUnit
open Routing
open Baardskeerder

let test_serialization () = 
  let repr =[("left"),"k";],"right" in
  let routing = Routing.build repr in
  Printf.printf "original=%s\n" (Routing.to_s routing);
  let b = Pack.make_output 127 in
  Routing.routing_to b routing ;
  let flat = Pack.close_output b in
  Printf.printf "flat = %S" flat;
  let input = Pack.make_input flat 4 in (* skip size *)
  let inflated = Routing.routing_from input in
  Printf.printf "reinflated=%s\n" (Routing.to_s inflated);
  OUnit.assert_equal routing inflated ~printer:Routing.to_s;
  ()
  
let test_change1 () = 
  let repr = ["left","k";], "right" in
  let r = Routing.build repr in
  let r2 = Routing.change r "left" "m" "right" in
  let () = Printf.printf "r2=%s\n" (Routing.to_s r2) in
  let n = Routing.find r2 "l" in
  OUnit.assert_equal ~printer:(fun s -> s) n "left"

let test_change2 () = 
  let repr = ["one","d";
	      "two","k";
	      "three","t";
	     ], "four" in
  let r  = Routing.build repr in
  let r2 = Routing.change r "three" "s" "four" in
  let () = Printf.printf "r =%s\n" (Routing.to_s r) in 
  let () = Printf.printf "r2=%s\n" (Routing.to_s r2) in
  let n = Routing.find r2 "s1" in
  OUnit.assert_equal ~printer:(fun s -> s) n "four"

let suite = "routing" >::: [
  "serialization" >:: test_serialization;
  "change1" >:: test_change1;
  "change2" >:: test_change2;
]
