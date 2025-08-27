<!---
This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.
You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

This project implements a **serial AES-128 encryption core** optimized for TinyTapeout's 1x1 tile constraint (~1000 logic gates). The design uses the Advanced Encryption Standard (AES) algorithm with 128-bit keys and blocks, processing data one byte at a time to minimize gate count while maintaining cryptographic security.

### AES Algorithm Implementation

The core implements the standard AES-128 encryption process:

- **Block Size**: 128 bits (16 bytes) arranged in a 4x4 matrix
- **Key Size**: 128 bits (16 bytes) 
- **Rounds**: 10 encryption rounds
- **Operations**: SubBytes (S-box substitution), ShiftRows (row shifting), MixColumns (column mixing), AddRoundKey (key XOR)

### Architecture Features

**Serial Processing**: Instead of parallel 128-bit operations, the design processes one byte at a time, dramatically reducing gate requirements while maintaining algorithmic correctness.

**Optimized S-box**: Uses a compact lookup table implementation for the SubBytes transformation, shared across all byte operations.

**State Machine Control**: A finite state machine manages four operational modes:
- Key loading (16 bytes via serial input)
- Plaintext loading (16 bytes via serial input) 
- Encryption processing (10 rounds of AES transformations)
- Ciphertext output (16 bytes via byte-addressable output)

**Memory Efficient**: Uses register arrays to store the 128-bit state and round keys, with simplified key scheduling optimized for area constraints.

## How to test

### Setup and Initialization

1. **Reset the system**: Assert `rst_n` low, then release high
2. **Set clock frequency**: Recommended 10 MHz for reliable serial operation

### Testing Procedure

#### Step 1: Load Encryption Key
Set ui[2:1] = 2'b00 (key load mode)

Set ui = 1 (start operation)

Clock in 16 key bytes sequentially via uio[7:0]

Each byte requires one clock cycle



#### Step 2: Load Plaintext Data  
Set ui[2:1] = 2'b01 (data load mode)

Set ui = 1 (start operation)

Clock in 16 plaintext bytes sequentially via uio[7:0]

Each byte requires one clock cycle



#### Step 3: Execute Encryption
Set ui[2:1] = 2'b10 (encrypt mode)

Set ui = 1 (start encryption)

Wait approximately 40-50 clock cycles for completion

Monitor processing status via internal state machine



#### Step 4: Read Encrypted Output
Set ui[2:1] = 2'b11 (output mode)

Set ui[7:3] to byte address (0-15)

Read encrypted byte from uo[7:0]

Repeat for all 16 output bytes


### Test Vectors

**Example Test Case**:
Key: 0x2b7e151628aed2a6abf7158809cf4f3c
Plain: 0x3243f6a8885a308d313198a2e0370734
Cipher: 0x3925841d02dc09fbdc118597196a0b32

text

### Verification Methods

- Compare output against known AES test vectors
- Verify each byte of ciphertext matches expected results
- Test with multiple key/plaintext combinations
- Validate state machine transitions and timing

## External hardware

This project is designed as a **standalone digital core** and does not require external hardware components. All functionality is contained within the TinyTapeout chip itself.

### Interface Requirements

**Power Supply**: Standard TinyTapeout 1.8V digital supply

**Clock Source**: External clock input via TinyTapeout's global clock network (recommended 10 MHz)

**I/O Connections**: All communication occurs through the standard TinyTapeout pin interface:
- 8 dedicated input pins (ui[7:0])
- 8 dedicated output pins (uo[7:0])  
- 8 bidirectional pins (uio[7:0]) used for data input

### Optional Testing Setup

For comprehensive testing and demonstration, consider:

**Microcontroller Interface**: Arduino, Raspberry Pi, or similar development board to:
- Generate test vectors and control signals
- Automate the encryption testing sequence
- Compare results against software AES implementation
- Provide user interface for interactive testing

**Logic Analyzer**: For debugging and timing verification of the serial communication protocol

**Development Board**: TinyTapeout carrier board provides all necessary connections and power regulation

### Software Tools

**Simulation**: Use standard Verilog simulators (ModelSim, Icarus Verilog) with the provided testbench

**Verification**: Python or C++ scripts to generate AES test vectors and validate outputs against reference implementations

No specialized cryptographic hardware or security modules are required - this is a educational/demonstration implementation suitable for learning AES principles and ASIC design techniques
