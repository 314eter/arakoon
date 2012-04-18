"""
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
"""

from .. import system_tests_common as C
from arakoon.ArakoonExceptions import *
import arakoon
import time
from nose.tools import *
#from pymonkey import q, i
import Compat as X

CONFIG = C.CONFIG
@C.with_custom_setup ( C.setup_1_node_forced_master, C.basic_teardown )
def test_start_stop_single_node_forced () :
    C.assert_running_nodes ( 1 )
    cluster = C._getCluster()
    cluster.stop() 
    C.assert_running_nodes ( 0 )
    cluster.start() 
    C.assert_running_nodes ( 1 )

@C.with_custom_setup ( C.setup_3_nodes_forced_master, C.basic_teardown )
def test_start_stop_three_nodes_forced () :
    cluster = C._getCluster()
    C.assert_running_nodes ( 3 )
    cluster.stop() 
    C.assert_running_nodes ( 0 )
    cluster.start() 
    C.assert_running_nodes ( 3 )

@C.with_custom_setup( C.default_setup, C.basic_teardown )        
def test_single_client_100_set_get_and_deletes() :
    C.iterate_n_times( 100, C.set_get_and_delete )
    
@C.with_custom_setup( C.setup_1_node_forced_master, C.basic_teardown)
def test_deploy_1_to_2():
    C.add_node_scenario (1)
    
@C.with_custom_setup( C.setup_2_nodes_forced_master, C.basic_teardown)
def test_deploy_2_to_3():
    C.add_node_scenario (2)

@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_range ():
    C.range_scenario ( 1000 )

@C.with_custom_setup( C.default_setup, C.basic_teardown)
def test_reverse_range_entries():
    C.reverse_range_entries_scenario(1000)


@C.with_custom_setup ( C.setup_1_node_forced_master, C.basic_teardown )
def test_large_value ():
    value = 'x' * (10 * 1024 * 1024)
    client = C.get_client()
    try:
        client.set ('some_key', value)
        raise Exception('this should have failed')
    except ArakoonException as inst:
        X.logging.info('inst=%s', inst)
    



    


    

@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_range_entries ():
    C.range_entries_scenario( 1000 )
    

@C.with_custom_setup(C.default_setup, C.basic_teardown)
def test_aSSert_scenario_1():
    client = C.get_client()
    client.set('x','x')
    try:
        client.aSSert('x','x') 
    except ArakoonException as ex:
        X.logging.error ( "Bad stuff happened: %s" % ex)
        assert_equals(True,False)

@C.with_custom_setup(C.default_setup, C.basic_teardown)
def test_aSSert_scenario_2():
    client = C.get_client()
    client.set('x','x')
    assert_raises( ArakoonAssertionFailed, client.aSSert, 'x', None)

@C.with_custom_setup(C.default_setup, C.basic_teardown)
def test_aSSert_scenario_3():
    client = C.get_client()
    client.set('x','x')
    ass = arakoon.ArakoonProtocol.Assert('x','x')
    seq = arakoon.ArakoonProtocol.Sequence()
    seq.addUpdate(ass)
    client.sequence(seq)

@C.with_custom_setup(C.setup_1_node_forced_master, C.basic_teardown)
def test_aSSert_sequences():
    client = C.get_client()
    client.set ('test_assert','test_assert')
    client.aSSert('test_assert', 'test_assert')    
    assert_raises(ArakoonAssertionFailed, 
                  client.aSSert, 
                  'test_assert',
                  'something_else')

    seq = arakoon.ArakoonProtocol.Sequence()
    seq.addAssert('test_assert','test_assert')
    seq.addSet('test_assert','changed')
    client.sequence(seq)

    v = client.get('test_assert')

    assert_equals(v, 'changed', "first_sequence failed")

    seq2 = arakoon.ArakoonProtocol.Sequence() 
    seq2.addAssert('test_assert','test_assert')
    seq2.addSet('test_assert','changed2')
    assert_raises(ArakoonAssertionFailed, 
                  client.sequence,
                  seq2)
    
    v = client.get('test_assert')
    assert_equals(v, 'changed', 'second_sequence: %s <> %s' % (v,'changed'))
    

@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_prefix ():
    C.prefix_scenario(1000)

def tes_and_set_scenario( start_suffix ): #tes is deliberate
    client = C.get_client()
    
    old_value_prefix = "old_"
    new_value_prefix = "new_"
    
    for i in range ( 1000 ) :
        
        old_value = old_value_prefix + CONFIG.value_format_str % ( i+start_suffix )
        new_value = new_value_prefix + CONFIG.value_format_str % ( i+start_suffix )
        key = CONFIG.key_format_str % ( i+start_suffix )
    
        client.set( key, old_value )
        set_value = client.testAndSet( key, old_value , new_value )
        assert_equals( set_value, old_value ) 
        
        set_value = client.get ( key )
        assert_equals( set_value, new_value )
    
        set_value = client.testAndSet( key, old_value, old_value )
        assert_equals( set_value, new_value )
    
        set_value = client.get ( key )
        assert_not_equals( set_value, old_value )
        
        try:
            client.delete( key )
        except ArakoonNotFound:
            logging.error ( "Caught not found for key %s" % key )
        assert_raises( ArakoonNotFound, client.get, key )
    
    client._dropConnections()


@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_test_and_set() :
    tes_and_set_scenario( 100000 )
    
@C.with_custom_setup( C.setup_3_nodes_forced_master , C.basic_teardown )
def test_who_master_fixed () :
    client = C.get_client()
    node = client.whoMaster()
    assert_equals ( node, CONFIG.node_names[0] ) 
    client._dropConnections()

@C.with_custom_setup( C.setup_3_nodes , C.basic_teardown )
def test_who_master () :
    client = C.get_client()
    node = client.whoMaster()
    assert_true ( node in CONFIG.node_names ) 
    client._dropConnections()

@C.with_custom_setup( C.setup_3_nodes_forced_master, C.basic_teardown )
def test_restart_single_slave_short ():
    C.restart_single_slave_scenario( 2, 100 )


def test_show_version () :
    cmd = [CONFIG.binary_full_path,'--version']
    X.logging.debug("cmd = %s", cmd)
    stdout = X.subprocess.check_output(cmd)
    X.logging.debug( "STDOUT: \n%s" % stdout )
    version = stdout.split('"') [1]
    assert_not_equals( "000000000000", version, "Invalid version 000000000000" )
    local_mods = version.find ("dirty") 
    assert_equals( local_mods, -1, "Invalid daemon, built with local modifications")

@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_delete_non_existing() :
    cli = C.get_client()
    try :
        cli.delete( 'non-existing' )
    except ArakoonNotFound as ex:
        ex_msg = "%s" % ex
        assert_equals( "'non-existing'", ex_msg, "Delete did not return the key, got: %s" % ex_msg)
    C.set_get_and_delete( cli, "k", "v")


@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_delete_non_existing_sequence() :
    cli = C.get_client()
    seq = arakoon.ArakoonProtocol.Sequence()
    seq.addDelete( 'non-existing' )
    try :
        cli.sequence( seq )
    except ArakoonNotFound as ex:
        ex_msg = "%s" % ex
        assert_equals( "'non-existing'", ex_msg, "Sequence did not return the key, got: %s" % ex_msg)
    C.set_get_and_delete( cli, "k", "v")

        
def sequence_scenario( start_suffix ):
    iter_size = 1000
    cli = C.get_client()
    
    start_key = CONFIG.key_format_str % start_suffix
    end_key = CONFIG.key_format_str % ( start_suffix + iter_size - 1 )
    seq = arakoon.ArakoonProtocol.Sequence()
    for i in range( iter_size ) :
        k = CONFIG.key_format_str % (i+start_suffix)
        v = CONFIG.value_format_str % (i+start_suffix) 
        seq.addSet(k, v)
        
    cli.sequence( seq )
    
    key_value_list = cli.range_entries( start_key, True, end_key, True )
    C.assert_key_value_list(start_suffix, iter_size , key_value_list )
    
    seq = arakoon.ArakoonProtocol.Sequence()
    for i in range( iter_size ) :
        k = CONFIG.key_format_str % (start_suffix + i) 
        seq.addDelete(k)
    cli.sequence( seq )
    
    key_value_list = cli.range_entries( start_key, True, end_key, True )
    assert_equal( len(key_value_list), 0, 
                  "Still keys in the store, should have been deleted" )
    
    for i in range( iter_size ) :
        k= CONFIG.key_format_str % (start_suffix + i)
        v = CONFIG.value_format_str % (start_suffix + i) 
        seq.addSet(k, v)
                    
    seq.addDelete( "non-existing" )
    assert_raises( ArakoonNotFound, cli.sequence, seq )
    key_value_list = cli.range_entries( start_key, True, end_key, True )
    assert_equal( len(key_value_list), 0, "There are keys in the store, should not be the case" )
    
    cli._dropConnections()
    
@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_sequence ():
    sequence_scenario( 10000 )


@C.with_custom_setup( C.setup_3_nodes , C.basic_teardown )   
def test_3_nodes_stop_all_start_slaves ():
    
    key = C.getRandomString()
    value = C.getRandomString() 
    
    cli = C.get_client()
    cli.set(key,value)
    master = cli.whoMaster()
    slaves = filter( lambda node: node != master, CONFIG.node_names )
    
    C.stop_all()
    for slave in slaves:
        C.startOne( slave )
    
    cli._dropConnections()
    cli = C.get_client()
    stored_value = cli.get( key )
    assert_equals( stored_value, value, 
                   "Stored value mismatch for key '%s' ('%s' != '%s')" % 
                   (key, value, stored_value) )
    
@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_get_storage_utilization():
    cl = C._getCluster()
    cli = C.get_client()
    cli.set('key','value')
    time.sleep(0.2)
    C.stop_all()
    
    def get_total_size( d ):
        assert_not_equals( d['log'], 0, "Log dir cannot be empty")
        assert_not_equals( d['db'], 0 , "Db dir cannot be empty")
        assert_not_equals( d['tlog'], 0, "Tlog dir cannot be empty")
        return d['log'] + d['tlog'] + d['db'] 
    
    X.logging.debug("Testing global utilization")
    d = cl.getStorageUtilization()
    total = get_total_size(d)
    X.logging.debug("Testing node 0 utilization")
    d = cl.getStorageUtilization( CONFIG.node_names[0] )
    n1 = get_total_size(d)
    X.logging.debug("Testing node 1 utilization")
    d = cl.getStorageUtilization( CONFIG.node_names[1] )
    n2 = get_total_size(d)
    X.logging.debug("Testing node 2 utilization")
    d = cl.getStorageUtilization( CONFIG.node_names[2] )
    n3 = get_total_size(d)
    sum = n1+n2+n3
    assert_equals(sum, total, 
                  "Sum of storage size per node (%d) should be same as total (%d)" % 
                  (sum,total))


@C.with_custom_setup( C.default_setup, C.basic_teardown )
def test_gather_evidence():
    data_base_dir = C.data_base_dir
    q = C.q
    cluster = C._getCluster()
    dest_file = '/'.join([data_base_dir, "evidence.tgz" ])
    dest_dir =  '/'.join([data_base_dir, "evidence"])
    destination = 'file://%s' % dest_file 
    cluster.gatherEvidence(destination, test = True)
    
    fs.targzUncompress(dest_file, dest_dir)
    nodes = X.listDirsInDir(dest_dir)
    files = []
    for node in nodes:
        files.extend(fs.listFilesInDir(node))
    assert_equals(len(nodes),3, "Did not get data from all nodes")
    assert_equals(len(files) > 12, True , "Did not gather enough files")

@C.with_custom_setup( C.default_setup, C.basic_teardown ) 
def test_get_key_count():
    cli = C.get_client()
    c = cli.getKeyCount()
    assert_equals(c, 0, "getKeyCount should return 0 but got %d" % c)
    test_size = 100
    C.iterate_n_times( test_size, C.simple_set )

    X.logging.debug ("cli's config = %s", cli._config)
    c = cli.getKeyCount()
    assert_equals(c, test_size, "getKeyCount should return %d but got %d" % 
                  (test_size, c) )

@C.with_custom_setup (C.setup_2_nodes, C.basic_teardown )
def test_download_db():
    C.iterate_n_times( 100, C.simple_set )
    cli = C.get_client()
    m = cli.whoMaster()
    clu = C._getCluster()
    assert_raises(Exception, clu.backupDb, m, "/tmp/backup")
    C.stop_all()
    
    n0 = CONFIG.node_names[0]
    n1 = CONFIG.node_names[1]
    C.startOne(n0)
    time.sleep(0.1)
    db_file = C.get_node_db_file (n1)
    clu.backupDb(n0, db_file)
    C.assert_running_nodes(1)
    C.stop_all()
    C.compare_stores(n0,n1)
    
@C.with_custom_setup( C.setup_3_nodes, C.basic_teardown )
def test_statistics():
    cli = C.get_client()
    stat_dict = cli.statistics()
    
    required_keys = [
       "start",
       "last", 
       "set_info",
       "get_info",
       "del_info",
       "seq_info",
       "mget_info",
       "tas_info",
       "op_info",
       "node_is",
    ]
    required_timing_keys = [
        "n",
        "min",
        "max",
        "avg",
        "var"
    ]
    
    for k in required_keys:
        assert_true( stat_dict.has_key(k), "Required key missing: %s" % k)
        if k.startswith("n_"):
            assert_equals( stat_dict[k], 0, "Operation counter should be 0, but is %d" % stat_dict[k] )
        if k.endswith( "_timing"):
            timing = stat_dict[k]
            for tk in required_timing_keys:
                assert_true( timing.has_key(tk), "Required key (%s) missing in time info (%s)" % (tk, k) )
                assert_equals( timing["max"], 0.0, 
                    "Wrong value for max timing of %s: %f != 0.0" %(k, timing["max"]))
                assert_equals( timing["avg"], 0.0, 
                    "Wrong value for avg timing of %s: %f != 0.0" %(k, timing["avg"]))
                assert_equals( timing["var"], 0.0, 
                    "Wrong value for var timing of %s: %f != 0.0" %(k, timing["var"]))
                assert_not_equals( timing["min"], 0.0, 
                    "Wrong value for min timing of %s: 0.0" %(k))

 
    key_list = list()
    seq = arakoon.ArakoonProtocol.Sequence()
    
    for i in range(10) :
        key = "key_%d" % i
        key2 = "key2_%d" % i
        val = "val_%d" % i
        key_list.append( key )
        cli.set(key, val)
        cli.get(key )
        cli.multiGet(key_list)
        seq.addSet(key2,val)
        seq.addDelete(key2)
        cli.sequence( seq )
        cli.testAndSet(key,None,val)
    for i in range(10):
        key = "key_%d" % i
        cli.delete(key)
    
    stat_dict = cli.statistics()
    
    for k in required_keys:
        assert_true( stat_dict.has_key(k), "Required key missing: %s" % k)
        if k.startswith("n_"):
            assert_not_equals( stat_dict[k], 0, 
                "Operation counter %s should be not be 0, but is." % k )
        if k.endswith( "_timing"):
            timing = stat_dict[k]
            for tk in required_timing_keys:
                assert_true( timing.has_key(tk), "Required key (%s) missing in time info (%s)" % (tk, k) )
                assert_not_equals( timing["max"], 0.0, 
                    "Wrong value for max timing of %s == 0.0" %k)
                assert_not_equals( timing["avg"], 0.0, 
                    "Wrong value for avg timing of %s == 0.0" % k)
                assert_not_equals( timing["var"], 0.0, 
                    "Wrong value for var timing of %s == 0.0" % k)
                assert_not_equals( timing["min"], 0.0, 
                    "Wrong value for min timing of %s == 0.0" % k)
    