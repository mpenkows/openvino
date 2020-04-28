import os
import pytest
import warnings
import numpy as np

from openvino.inference_engine import IENetwork, IENetLayer, DataPtr, LayersStatsMap, LayerStats, IECore
from conftest import model_path

test_net_xml, test_net_bin = model_path()

def test_create_ie_network_deprecated():
    with warnings.catch_warnings(record=True) as w:
        net = IENetwork(model=test_net_xml, weights=test_net_bin)
        assert isinstance(net, IENetwork)
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "Reading network using constructor is deprecated. " \
               "Please, use IECore.read_network() method instead" in str(w[0].message)


def test_incorrect_xml_deprecated():
    with warnings.catch_warnings(record=True) as w:
        with pytest.raises(Exception) as e:
            IENetwork(model="./model.xml", weights=test_net_bin)
        assert "Path to the model ./model.xml doesn't exist or it's a directory" in str(e.value)
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "Reading network using constructor is deprecated. " \
               "Please, use IECore.read_network() method instead" in str(w[0].message)


def test_incorrect_bin_deprecated():
    with warnings.catch_warnings(record=True) as w:
        with pytest.raises(Exception) as e:
            IENetwork(model=test_net_xml, weights="./model.bin")
        assert "Path to the weights ./model.bin doesn't exist or it's a directory" in str(e.value)
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "Reading network using constructor is deprecated. " \
               "Please, use IECore.read_network() method instead" in str(w[0].message)


@pytest.mark.skip(reason="name) returns wrong name, problem somewhere in ngraph")
def test_name():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    assert net.name == "model"


def test_inputs():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    assert isinstance(net.inputs['data'], DataPtr)
    assert net.inputs['data'].layout == "NCHW"
    assert net.inputs['data'].precision == "FP32"
    assert net.inputs['data'].shape == [1, 3, 32, 32]


def test_input_precision_setter():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    assert net.inputs['data'].layout == "NCHW"
    net.inputs['data'].layout = "NHWC"
    assert net.inputs['data'].layout == "NHWC"


def test_input_layout_setter():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    assert net.inputs['data'].precision == "FP32"
    net.inputs['data'].precision = "I8"
    assert net.inputs['data'].precision == "I8"


def test_input_unsupported_precision_setter():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    with pytest.raises(ValueError) as e:
        net.inputs['data'].precision = "BLA"
    assert "Unsupported precision BLA! List of supported precisions: " in str(e.value)


def test_input_unsupported_layout_setter():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    with pytest.raises(ValueError) as e:
        net.inputs['data'].layout = "BLA"
    assert "Unsupported layout BLA! List of supported layouts: " in str(e.value)


def test_outputs():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    assert isinstance(net.outputs['fc_out'], DataPtr)
    assert net.outputs['fc_out'].layout == "NC"
    assert net.outputs['fc_out'].precision == "FP32"
    assert net.outputs['fc_out'].shape == [1, 10]


def test_output_precision_setter():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    assert net.outputs['fc_out'].precision == "FP32"
    net.outputs['fc_out'].precision = "I8"
    assert net.outputs['fc_out'].precision == "I8"


def test_output_unsupported_precision_setter():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    with pytest.raises(ValueError) as e:
        net.outputs['fc_out'].precision = "BLA"
    assert "Unsupported precision BLA! List of supported precisions: " in str(e.value)


def test_add_ouputs():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    net.add_outputs('28/Reshape')
    net.add_outputs(['29/WithoutBiases'])
    assert sorted(net.outputs) == ['28/Reshape', '29/WithoutBiases', 'fc_out']


def test_add_outputs_with_port():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    net.add_outputs(('28/Reshape', 0))
    net.add_outputs([('29/WithoutBiases', 0)])
    assert sorted(net.outputs) == ['28/Reshape', '29/WithoutBiases', 'fc_out']


def test_add_outputs_with_and_without_port():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    net.add_outputs('28/Reshape')
    net.add_outputs([('29/WithoutBiases', 0)])
    assert sorted(net.outputs) == ['28/Reshape', '29/WithoutBiases', 'fc_out']


def test_batch_size_getter():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    assert net.batch_size == 1


def test_batch_size_setter():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    net.batch_size = 4
    assert net.batch_size == 4
    assert net.inputs['data'].shape == [4, 3, 32, 32]

def test_batch_size_after_reshape():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    net.reshape({'data' : [4, 3, 32, 32]})
    assert net.batch_size == 4
    assert net.inputs['data'].shape == [4, 3, 32, 32]
    net.reshape({'data' : [8, 3, 32, 32]})
    assert net.batch_size == 8
    assert net.inputs['data'].shape == [8, 3, 32, 32]

def test_layers():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    layers_name = [key for key in net.layers]
    assert sorted(layers_name) == ['19/Fused_Add_', '21', '22', '23', '24/Fused_Add_', '26', '27', '29', 'data', 'fc_out']
    assert isinstance(net.layers['19/Fused_Add_'], IENetLayer)


def test_get_stats_deprecated():
    with warnings.catch_warnings(record=True) as w:
        ie = IECore()
        net = ie.read_network(model=test_net_xml, weights=test_net_bin)
        stats = net.stats
        assert isinstance(stats, LayersStatsMap)
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "stats property of IENetwork is deprecated." in str(w[-1].message)


@pytest.mark.skip(reason="Test is failed due-to ngraph conversion")
def test_set_new_stats_deprecated():
    with warnings.catch_warnings(record=True) as w:
        ie = IECore()
        net = ie.read_network(model=test_net_xml, weights=test_net_bin)
        new_stats = LayerStats(min=(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0),
                               max=(10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0))
        stats = net.stats
        stats.update({"fc_out": new_stats})
        assert net.stats["fc_out"].min == new_stats.min
        assert net.stats["fc_out"].max == new_stats.max
        assert len(w) == 3
        for warns in w:
            assert issubclass(warns.category, DeprecationWarning)
            assert "stats property of IENetwork is deprecated." in str(warns.message)


@pytest.mark.skip(reason="Test is failed due-to ngraph conversion")
def test_update_stats_deprecated():
    with warnings.catch_warnings(record=True) as w:
        ie = IECore()
        net = ie.read_network(model=test_net_xml, weights=test_net_bin)
        initial_stats = LayerStats(min=(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0),
                                   max=(10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0))
        stats = net.stats
        stats.update({"fc_out": initial_stats})
        new_stats = LayerStats(min=(10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0),
                               max=(10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0))
        stats.update({"fc_out": new_stats})
        assert net.stats["fc_out"].min == new_stats.min
        assert net.stats["fc_out"].max == new_stats.max
        assert len(w) == 3
        for warns in w:
            assert issubclass(warns.category, DeprecationWarning)
            assert "stats property of IENetwork is deprecated." in str(warns.message)


@pytest.mark.skip(reason="Test is failed due-to ngraph conversion")
def test_serialize():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    net.serialize("./serialized_net.xml", "./serialized_net.bin")
    serialized_net = ie.read_network(model="./serialized_net.xml", weights="./serialized_net.bin")
    assert net.layers.keys() == serialized_net.layers.keys()
    os.remove("./serialized_net.xml")
    os.remove("./serialized_net.bin")


def test_reshape():
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    net.reshape({"data": (2, 3, 32, 32)})


def test_read_net_from_buffer_deprecated():
    with warnings.catch_warnings(record=True) as w:
        with open(test_net_bin, 'rb') as f:
            bin = f.read()
        with open(test_net_xml, 'rb') as f:
            xml = f.read()
        net = IENetwork(model=xml, weights=bin, init_from_buffer=True)
        assert isinstance(net, IENetwork)
        assert len(w) == 1
        assert issubclass(w[-1].category, DeprecationWarning)
        assert "Reading network using constructor is deprecated. " \
               "Please, use IECore.read_network() method instead" in str(w[0].message)


def test_net_from_buffer_valid_deprecated():
    with warnings.catch_warnings(record=True) as w:
        with open(test_net_bin, 'rb') as f:
            bin = f.read()
        with open(test_net_xml, 'rb') as f:
            xml = f.read()
        net = IENetwork(model=xml, weights=bin, init_from_buffer=True)
        net2 = IENetwork(model=test_net_xml, weights=test_net_bin)
        for name, l in net.layers.items():
            for blob, data in l.blobs.items():
                assert np.allclose(data, net2.layers[name].blobs[blob]), \
                    "Incorrect weights for layer {} and blob {}".format(name, blob)
        assert len(w) == 2
        for warns in w:
            assert issubclass(warns.category, DeprecationWarning)
            assert "Reading network using constructor is deprecated. " \
                   "Please, use IECore.read_network() method instead" in str(warns.message)


def test_multi_out_data():
    # Regression test CVS-23965
    # Check that DataPtr for all output layers not copied between outputs map  items
    ie = IECore()
    net = ie.read_network(model=test_net_xml, weights=test_net_bin)
    net.add_outputs(['28/Reshape'])
    assert "28/Reshape" in net.outputs and "fc_out" in net.outputs
    assert isinstance(net.outputs["28/Reshape"], DataPtr)
    assert isinstance(net.outputs["fc_out"], DataPtr)
    assert net.outputs["28/Reshape"].name == "28/Reshape" and net.outputs["28/Reshape"].shape == [1, 5184]
    assert net.outputs["fc_out"].name == "fc_out" and net.outputs["fc_out"].shape == [1, 10]
    pass