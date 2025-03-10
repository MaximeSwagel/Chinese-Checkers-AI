#include <x86intrin.h>
#include <stdint.h>

// Python isn't suited for this
// compile with "gcc -mbmi2 -shared -o bmi2_bitops.so -fPIC bmi2_bitops.c"

// PEXT: Extracts bits from 'source' using 'mask' and packs them
uint64_t pext_native(uint64_t source, uint64_t mask) {
    return _pext_u64(source, mask);
}

// PDEP: Expands bits into 'mask' positions from a compacted bit pattern
uint64_t pdep_native(uint64_t source, uint64_t mask) {
    return _pdep_u64(source, mask);
}