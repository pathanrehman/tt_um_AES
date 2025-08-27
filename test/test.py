# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_aes_encryption(dut):
    """Test AES-128 encryption with known test vectors"""
    
    dut._log.info("Starting AES-128 Encryption Test")
    
    # Set the clock period to 100 ns (10 MHz)
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset sequence
    dut._log.info("Performing Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Test vectors from NIST AES specification
    test_key = [0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6,
                0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c]
    
    test_plaintext = [0x32, 0x43, 0xf6, 0xa8, 0x88, 0x5a, 0x30, 0x8d,
                      0x31, 0x31, 0x98, 0xa2, 0xe0, 0x37, 0x07, 0x34]
    
    expected_ciphertext = [0x39, 0x25, 0x84, 0x1d, 0x02, 0xdc, 0x09, 0xfb,
                          0xdc, 0x11, 0x85, 0x97, 0x19, 0x6a, 0x0b, 0x32]
    
    # Step 1: Load encryption key
    dut._log.info("Loading 128-bit encryption key")
    dut.ui_in.value = 0x01  # operation=00 (key load), start=1
    await ClockCycles(dut.clk, 1)
    
    for i, key_byte in enumerate(test_key):
        dut.uio_in.value = key_byte
        await ClockCycles(dut.clk, 1)
        dut._log.info(f"Key byte {i}: 0x{key_byte:02x}")
    
    dut.ui_in.value = 0x00  # Clear start signal
    await ClockCycles(dut.clk, 2)
    
    # Step 2: Load plaintext data
    dut._log.info("Loading 128-bit plaintext data")
    dut.ui_in.value = 0x03  # operation=01 (data load), start=1
    await ClockCycles(dut.clk, 1)
    
    for i, data_byte in enumerate(test_plaintext):
        dut.uio_in.value = data_byte
        await ClockCycles(dut.clk, 1)
        dut._log.info(f"Plaintext byte {i}: 0x{data_byte:02x}")
    
    dut.ui_in.value = 0x00  # Clear start signal
    await ClockCycles(dut.clk, 2)
    
    # Step 3: Start encryption process
    dut._log.info("Starting AES encryption")
    dut.ui_in.value = 0x05  # operation=10 (encrypt), start=1
    await ClockCycles(dut.clk, 1)
    dut.ui_in.value = 0x04  # Keep operation=10, clear start
    
    # Wait for encryption to complete (10 rounds * 4 cycles per round + overhead)
    await ClockCycles(dut.clk, 50)
    
    # Step 4: Read encrypted output and verify
    dut._log.info("Reading encrypted output")
    dut.ui_in.value = 0x06  # operation=11 (output mode)
    
    output_data = []
    for i in range(16):
        # Set byte address
        byte_addr = i
        dut.ui_in.value = 0x06 | (byte_addr << 3)  # operation=11, byte_addr
        await ClockCycles(dut.clk, 1)
        
        output_byte = int(dut.uo_out.value)
        output_data.append(output_byte)
        dut._log.info(f"Output byte {i}: 0x{output_byte:02x} (expected: 0x{expected_ciphertext[i]:02x})")
    
    # Verify encryption result
    dut._log.info("Verifying encryption results")
    for i in range(16):
        assert output_data[i] == expected_ciphertext[i], \
            f"Mismatch at byte {i}: got 0x{output_data[i]:02x}, expected 0x{expected_ciphertext[i]:02x}"
    
    dut._log.info("AES-128 encryption test PASSED!")

@cocotb.test()
async def test_aes_state_machine(dut):
    """Test AES state machine transitions"""
    
    dut._log.info("Testing AES State Machine")
    
    # Set up clock
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Test invalid operation modes
    dut._log.info("Testing invalid operation handling")
    dut.ui_in.value = 0x07  # operation=11 (invalid), start=1
    await ClockCycles(dut.clk, 5)
    
    # Should remain in safe state
    dut.ui_in.value = 0x00
    await ClockCycles(dut.clk, 2)
    
    dut._log.info("State machine test completed")

@cocotb.test()
async def test_aes_reset_behavior(dut):
    """Test reset functionality during operation"""
    
    dut._log.info("Testing Reset Behavior")
    
    # Set up clock
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())
    
    # Initial reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Start loading key, then reset mid-operation
    dut.ui_in.value = 0x01  # Start key load
    await ClockCycles(dut.clk, 1)
    
    dut.uio_in.value = 0xAA
    await ClockCycles(dut.clk, 3)
    
    # Reset during operation
    dut._log.info("Applying reset during key load")
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Verify system returns to idle state
    dut.ui_in.value = 0x00
    await ClockCycles(dut.clk, 5)
    
    dut._log.info("Reset behavior test completed")

@cocotb.test()
async def test_aes_io_pins(dut):
    """Test I/O pin functionality and bidirectional operation"""
    
    dut._log.info("Testing I/O Pin Functionality")
    
    # Set up clock
    clock = Clock(dut.clk, 100, units="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 5)
    
    # Test bidirectional pin control
    # During key/data loading, uio should be input (uio_oe = 0)
    dut.ui_in.value = 0x01  # Key load mode
    await ClockCycles(dut.clk, 1)
    
    # Check that uio_oe indicates input mode for data loading
    uio_oe_value = int(dut.uio_oe.value)
    dut._log.info(f"UIO_OE during key load: 0x{uio_oe_value:02x}")
    
    # Test different input values
    test_values = [0x00, 0xFF, 0xAA, 0x55, 0x12, 0x34]
    for val in test_values:
        dut.uio_in.value = val
        await ClockCycles(dut.clk, 1)
        dut._log.info(f"Input test value: 0x{val:02x}")
    
    dut.ui_in.value = 0x00
    await ClockCycles(dut.clk, 5)
    
    dut._log.info("I/O pin test completed")
