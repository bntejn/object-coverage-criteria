#!/bin/bash

function test1 {
    pin -t obj-intel64/PinCov.so -- ./tests/o0 tests/obsnop_tc_0.csv
}

function test_infusion_o2 {
    pin -t obj-intel64/PinCov.so -- ./tests/infusion_o2 tests/infusion.mcdc_tests.csv
}

test_infusion_o2
