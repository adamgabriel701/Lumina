; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Map" = type {i64*, i64*, i64, i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"GC_malloc"(i64 %".1")

declare void @"GC_init"()

declare void @"GC_free"(i8* %".1")

declare i8* @"strcpy"(i8* %".1", i8* %".2")

declare i8* @"strcat"(i8* %".1", i8* %".2")

declare i64 @"strlen"(i8* %".1")

declare i32 @"snprintf"(i8* %".1", i64 %".2", i8* %".3", ...)

declare i8* @"strstr"(i8* %".1", i8* %".2")

declare i32 @"strncmp"(i8* %".1", i8* %".2", i64 %".3")

declare i64 @"atoi"(i8* %".1")

declare i32 @"strcmp"(i8* %".1", i8* %".2")

declare i8* @"strncpy"(i8* %".1", i8* %".2", i64 %".3")

@"stdin" = external global i8*
@"stdout" = external global i8*
@"stderr" = external global i8*
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [26 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"new_map_call" = call %"Map"* @"new_map"()
  %"m" = alloca %"Map"*
  store %"Map"* %"new_map_call", %"Map"** %"m"
  %"m_load" = load %"Map"*, %"Map"** %"m"
  call void @"Map_insert"(%"Map"* %"m_load", i64 10, i64 100)
  %"m_load.1" = load %"Map"*, %"Map"** %"m"
  call void @"Map_insert"(%"Map"* %"m_load.1", i64 26, i64 200)
  %"m_load.2" = load %"Map"*, %"Map"** %"m"
  call void @"Map_insert"(%"Map"* %"m_load.2", i64 42, i64 999)
  %".11" = bitcast [10 x i8]* @"str_3" to i8*
  %".12" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".12", i8* %".11")
  %"m_load.3" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call" = call i64 @"Map_get"(%"Map"* %"m_load.3", i64 10)
  %".13" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".13")
  %".14" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".14", i64 %"Map_get_call")
  %".15" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [10 x i8]* @"str_8" to i8*
  %".17" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".17", i8* %".16")
  %"m_load.4" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call.1" = call i64 @"Map_get"(%"Map"* %"m_load.4", i64 26)
  %".18" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %".19" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".19", i64 %"Map_get_call.1")
  %".20" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %".21" = bitcast [10 x i8]* @"str_13" to i8*
  %".22" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".22", i8* %".21")
  %"m_load.5" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call.2" = call i64 @"Map_get"(%"Map"* %"m_load.5", i64 42)
  %".23" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %".24" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".24", i64 %"Map_get_call.2")
  %".25" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".25")
  %".26" = bitcast [10 x i8]* @"str_18" to i8*
  %".27" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".27", i8* %".26")
  %"m_load.6" = load %"Map"*, %"Map"** %"m"
  %"Map_get_call.3" = call i64 @"Map_get"(%"Map"* %"m_load.6", i64 99)
  %".28" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".28")
  %".29" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".29", i64 %"Map_get_call.3")
  %".30" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define i64 @"_map_hash"(i64 %".1", i64 %".2")
{
_map_hash_entry:
  %"key" = alloca i64
  store i64 %".1", i64* %"key"
  %"cap" = alloca i64
  store i64 %".2", i64* %"cap"
  br label %"_map_hash_body"
_map_hash_body:
  %"key_load" = load i64, i64* %"key"
  %"cap_load" = load i64, i64* %"cap"
  %"sub" = sub i64 %"cap_load", 1
  %"bitand" = and i64 %"key_load", %"sub"
  ret i64 %"bitand"
}

define void @"Map_rehash"(%"Map"* %".1")
{
Map_rehash_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  br label %"Map_rehash_body"
Map_rehash_body:
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".5" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".5"
  %"old_keys" = alloca i64*
  store i64* %"keys_load", i64** %"old_keys"
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".7" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 1
  %"values_load" = load i64*, i64** %".7"
  %"old_values" = alloca i64*
  store i64* %"values_load", i64** %"old_values"
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  %".9" = getelementptr %"Map", %"Map"* %"self_load.2", i32 0, i32 3
  %"cap_load" = load i64, i64* %".9"
  %"old_cap" = alloca i64
  store i64 %"cap_load", i64* %"old_cap"
  %"old_cap_load" = load i64, i64* %"old_cap"
  %"mul" = mul i64 %"old_cap_load", 2
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %"cap_ptr" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 3
  store i64 %"mul", i64* %"cap_ptr"
  %"self_load.4" = load %"Map"*, %"Map"** %"self"
  %".12" = getelementptr %"Map", %"Map"* %"self_load.4", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".12"
  %"alloc_size" = mul i64 %"cap_load.1", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"self_load.5" = load %"Map"*, %"Map"** %"self"
  %"keys_ptr" = getelementptr %"Map", %"Map"* %"self_load.5", i32 0, i32 0
  %"keys_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"keys_bitcast", i64** %"keys_ptr"
  %"self_load.6" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.6", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".14"
  %"alloc_size.1" = mul i64 %"cap_load.2", 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"self_load.7" = load %"Map"*, %"Map"** %"self"
  %"values_ptr" = getelementptr %"Map", %"Map"* %"self_load.7", i32 0, i32 1
  %"values_bitcast" = bitcast i8* %"alloc_call.1" to i64*
  store i64* %"values_bitcast", i64** %"values_ptr"
  %"self_load.8" = load %"Map"*, %"Map"** %"self"
  %"size_ptr" = getelementptr %"Map", %"Map"* %"self_load.8", i32 0, i32 2
  store i64 0, i64* %"size_ptr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"self_load.9" = load %"Map"*, %"Map"** %"self"
  %".19" = getelementptr %"Map", %"Map"* %"self_load.9", i32 0, i32 3
  %"cap_load.3" = load i64, i64* %".19"
  %"icmp" = icmp slt i64 %"i_load", %"cap_load.3"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"neg" = sub i64 0, 1
  %"self_load.10" = load %"Map"*, %"Map"** %"self"
  %".21" = getelementptr %"Map", %"Map"* %"self_load.10", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".21"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"i_load.1"
  store i64 %"neg", i64* %"idx_ptr"
  %"self_load.11" = load %"Map"*, %"Map"** %"self"
  %".23" = getelementptr %"Map", %"Map"* %"self_load.11", i32 0, i32 1
  %"values_load.1" = load i64*, i64** %".23"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr.1" = getelementptr i64, i64* %"values_load.1", i64 %"i_load.2"
  store i64 0, i64* %"idx_ptr.1"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"i.1" = alloca i64
  store i64 0, i64* %"i.1"
  br label %"while_cond.1"
while_cond.1:
  %"i_load.4" = load i64, i64* %"i.1"
  %"old_cap_load.1" = load i64, i64* %"old_cap"
  %"icmp.1" = icmp slt i64 %"i_load.4", %"old_cap_load.1"
  br i1 %"icmp.1", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"old_keys_load" = load i64*, i64** %"old_keys"
  %"i_load.5" = load i64, i64* %"i.1"
  %".30" = getelementptr i64, i64* %"old_keys_load", i64 %"i_load.5"
  %"ptr_idx_load" = load i64, i64* %".30"
  %"neg.1" = sub i64 0, 1
  %"icmp.2" = icmp ne i64 %"ptr_idx_load", %"neg.1"
  br i1 %"icmp.2", label %"and_rhs", label %"and_end"
while_end.1:
  ret void
and_rhs:
  %"old_keys_load.1" = load i64*, i64** %"old_keys"
  %"i_load.6" = load i64, i64* %"i.1"
  %".32" = getelementptr i64, i64* %"old_keys_load.1", i64 %"i_load.6"
  %"ptr_idx_load.1" = load i64, i64* %".32"
  %"neg.2" = sub i64 0, 2
  %"icmp.3" = icmp ne i64 %"ptr_idx_load.1", %"neg.2"
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_body.1"], [%"icmp.3", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  %"self_load.12" = load %"Map"*, %"Map"** %"self"
  %"old_keys_load.2" = load i64*, i64** %"old_keys"
  %"i_load.7" = load i64, i64* %"i.1"
  %".35" = getelementptr i64, i64* %"old_keys_load.2", i64 %"i_load.7"
  %"ptr_idx_load.2" = load i64, i64* %".35"
  %"old_values_load" = load i64*, i64** %"old_values"
  %"i_load.8" = load i64, i64* %"i.1"
  %".36" = getelementptr i64, i64* %"old_values_load", i64 %"i_load.8"
  %"ptr_idx_load.3" = load i64, i64* %".36"
  call void @"Map_insert"(%"Map"* %"self_load.12", i64 %"ptr_idx_load.2", i64 %"ptr_idx_load.3")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.9" = load i64, i64* %"i.1"
  %"add.1" = add i64 %"i_load.9", 1
  store i64 %"add.1", i64* %"i.1"
  br label %"while_cond.1"
}

define void @"Map_insert"(%"Map"* %".1", i64 %".2", i64 %".3")
{
Map_insert_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  %"value" = alloca i64
  store i64 %".3", i64* %"value"
  br label %"Map_insert_body"
Map_insert_body:
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".9" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 2
  %"size_load" = load i64, i64* %".9"
  %"mul" = mul i64 %"size_load", 4
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".10" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 3
  %"cap_load" = load i64, i64* %".10"
  %"mul.1" = mul i64 %"cap_load", 3
  %"icmp" = icmp sge i64 %"mul", %"mul.1"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  call void @"Map_rehash"(%"Map"* %"self_load.2")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"key_load" = load i64, i64* %"key"
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".14"
  %"_map_hash_call" = call i64 @"_map_hash"(i64 %"key_load", i64 %"cap_load.1")
  %"idx" = alloca i64
  store i64 %"_map_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  %"neg" = sub i64 0, 1
  %"first_tombstone" = alloca i64
  store i64 %"neg", i64* %"first_tombstone"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.4" = load %"Map"*, %"Map"** %"self"
  %".20" = getelementptr %"Map", %"Map"* %"self_load.4", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".20"
  %"icmp.1" = icmp slt i64 %"probes_load", %"cap_load.2"
  br i1 %"icmp.1", label %"while_body", label %"while_end"
while_body:
  %"self_load.5" = load %"Map"*, %"Map"** %"self"
  %".22" = getelementptr %"Map", %"Map"* %"self_load.5", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".22"
  %"i_load" = load i64, i64* %"i"
  %".23" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".23"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg.1" = sub i64 0, 1
  %"icmp.2" = icmp eq i64 %"k_load", %"neg.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
while_end:
  ret void
if_then.1:
  %"first_tombstone_load" = load i64, i64* %"first_tombstone"
  %"neg.2" = sub i64 0, 1
  %"icmp.3" = icmp ne i64 %"first_tombstone_load", %"neg.2"
  br i1 %"icmp.3", label %"if_then.2", label %"if_else.2"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"k_load.1" = load i64, i64* %"k"
  %"neg.3" = sub i64 0, 2
  %"icmp.4" = icmp eq i64 %"k_load.1", %"neg.3"
  br i1 %"icmp.4", label %"if_then.3", label %"if_else.3"
if_then.2:
  %"key_load.1" = load i64, i64* %"key"
  %"self_load.6" = load %"Map"*, %"Map"** %"self"
  %".27" = getelementptr %"Map", %"Map"* %"self_load.6", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".27"
  %"first_tombstone_load.1" = load i64, i64* %"first_tombstone"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"first_tombstone_load.1"
  store i64 %"key_load.1", i64* %"idx_ptr"
  %"value_load" = load i64, i64* %"value"
  %"self_load.7" = load %"Map"*, %"Map"** %"self"
  %".29" = getelementptr %"Map", %"Map"* %"self_load.7", i32 0, i32 1
  %"values_load" = load i64*, i64** %".29"
  %"first_tombstone_load.2" = load i64, i64* %"first_tombstone"
  %"idx_ptr.1" = getelementptr i64, i64* %"values_load", i64 %"first_tombstone_load.2"
  store i64 %"value_load", i64* %"idx_ptr.1"
  br label %"if_end.2"
if_else.2:
  %"key_load.2" = load i64, i64* %"key"
  %"self_load.8" = load %"Map"*, %"Map"** %"self"
  %".32" = getelementptr %"Map", %"Map"* %"self_load.8", i32 0, i32 0
  %"keys_load.2" = load i64*, i64** %".32"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr.2" = getelementptr i64, i64* %"keys_load.2", i64 %"i_load.1"
  store i64 %"key_load.2", i64* %"idx_ptr.2"
  %"value_load.1" = load i64, i64* %"value"
  %"self_load.9" = load %"Map"*, %"Map"** %"self"
  %".34" = getelementptr %"Map", %"Map"* %"self_load.9", i32 0, i32 1
  %"values_load.1" = load i64*, i64** %".34"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr.3" = getelementptr i64, i64* %"values_load.1", i64 %"i_load.2"
  store i64 %"value_load.1", i64* %"idx_ptr.3"
  br label %"if_end.2"
if_end.2:
  %"self_load.10" = load %"Map"*, %"Map"** %"self"
  %".37" = getelementptr %"Map", %"Map"* %"self_load.10", i32 0, i32 2
  %"size_load.1" = load i64, i64* %".37"
  %"add" = add i64 %"size_load.1", 1
  %"self_load.11" = load %"Map"*, %"Map"** %"self"
  %"size_ptr" = getelementptr %"Map", %"Map"* %"self_load.11", i32 0, i32 2
  store i64 %"add", i64* %"size_ptr"
  ret void
if_then.3:
  %"first_tombstone_load.3" = load i64, i64* %"first_tombstone"
  %"neg.4" = sub i64 0, 1
  %"icmp.5" = icmp eq i64 %"first_tombstone_load.3", %"neg.4"
  br i1 %"icmp.5", label %"if_then.4", label %"if_else.4"
if_else.3:
  %"k_load.2" = load i64, i64* %"k"
  %"key_load.3" = load i64, i64* %"key"
  %"icmp.6" = icmp eq i64 %"k_load.2", %"key_load.3"
  br i1 %"icmp.6", label %"if_then.5", label %"if_else.5"
if_end.3:
  %"i_load.5" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.5", 1
  %"self_load.13" = load %"Map"*, %"Map"** %"self"
  %".53" = getelementptr %"Map", %"Map"* %"self_load.13", i32 0, i32 3
  %"cap_load.3" = load i64, i64* %".53"
  %"sub" = sub i64 %"cap_load.3", 1
  %"bitand" = and i64 %"add.1", %"sub"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.2" = add i64 %"probes_load.1", 1
  store i64 %"add.2", i64* %"probes"
  br label %"while_cond"
if_then.4:
  %"i_load.3" = load i64, i64* %"i"
  store i64 %"i_load.3", i64* %"first_tombstone"
  br label %"if_end.4"
if_else.4:
  br label %"if_end.4"
if_end.4:
  br label %"if_end.3"
if_then.5:
  %"value_load.2" = load i64, i64* %"value"
  %"self_load.12" = load %"Map"*, %"Map"** %"self"
  %".48" = getelementptr %"Map", %"Map"* %"self_load.12", i32 0, i32 1
  %"values_load.2" = load i64*, i64** %".48"
  %"i_load.4" = load i64, i64* %"i"
  %"idx_ptr.4" = getelementptr i64, i64* %"values_load.2", i64 %"i_load.4"
  store i64 %"value_load.2", i64* %"idx_ptr.4"
  ret void
if_else.5:
  br label %"if_end.5"
if_end.5:
  br label %"if_end.3"
}

define i64 @"Map_get"(%"Map"* %".1", i64 %".2")
{
Map_get_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Map_get_body"
Map_get_body:
  %"key_load" = load i64, i64* %"key"
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".7" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 3
  %"cap_load" = load i64, i64* %".7"
  %"_map_hash_call" = call i64 @"_map_hash"(i64 %"key_load", i64 %"cap_load")
  %"idx" = alloca i64
  store i64 %"_map_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".12" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"probes_load", %"cap_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.2", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".14"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".15"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg" = sub i64 0, 1
  %"icmp.1" = icmp eq i64 %"k_load", %"neg"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"neg.2" = sub i64 0, 1
  ret i64 %"neg.2"
if_then:
  %"neg.1" = sub i64 0, 1
  ret i64 %"neg.1"
if_else:
  br label %"if_end"
if_end:
  %"k_load.1" = load i64, i64* %"k"
  %"key_load.1" = load i64, i64* %"key"
  %"icmp.2" = icmp eq i64 %"k_load.1", %"key_load.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %".21" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 1
  %"values_load" = load i64*, i64** %".21"
  %"i_load.1" = load i64, i64* %"i"
  %".22" = getelementptr i64, i64* %"values_load", i64 %"i_load.1"
  %"ptr_idx_load.1" = load i64, i64* %".22"
  ret i64 %"ptr_idx_load.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %"self_load.4" = load %"Map"*, %"Map"** %"self"
  %".25" = getelementptr %"Map", %"Map"* %"self_load.4", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".25"
  %"sub" = sub i64 %"cap_load.2", 1
  %"bitand" = and i64 %"add", %"sub"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.1" = add i64 %"probes_load.1", 1
  store i64 %"add.1", i64* %"probes"
  br label %"while_cond"
}

define i64 @"Map_contains"(%"Map"* %".1", i64 %".2")
{
Map_contains_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Map_contains_body"
Map_contains_body:
  %"key_load" = load i64, i64* %"key"
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".7" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 3
  %"cap_load" = load i64, i64* %".7"
  %"_map_hash_call" = call i64 @"_map_hash"(i64 %"key_load", i64 %"cap_load")
  %"idx" = alloca i64
  store i64 %"_map_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".12" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"probes_load", %"cap_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.2", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".14"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".15"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg" = sub i64 0, 1
  %"icmp.1" = icmp eq i64 %"k_load", %"neg"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret i64 0
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"k_load.1" = load i64, i64* %"k"
  %"key_load.1" = load i64, i64* %"key"
  %"icmp.2" = icmp eq i64 %"k_load.1", %"key_load.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  ret i64 1
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.1" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.1", 1
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %".23" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".23"
  %"sub" = sub i64 %"cap_load.2", 1
  %"bitand" = and i64 %"add", %"sub"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.1" = add i64 %"probes_load.1", 1
  store i64 %"add.1", i64* %"probes"
  br label %"while_cond"
}

define i64 @"Map_remove"(%"Map"* %".1", i64 %".2")
{
Map_remove_entry:
  %"self" = alloca %"Map"*
  store %"Map"* %".1", %"Map"** %"self"
  %"key" = alloca i64
  store i64 %".2", i64* %"key"
  br label %"Map_remove_body"
Map_remove_body:
  %"key_load" = load i64, i64* %"key"
  %"self_load" = load %"Map"*, %"Map"** %"self"
  %".7" = getelementptr %"Map", %"Map"* %"self_load", i32 0, i32 3
  %"cap_load" = load i64, i64* %".7"
  %"_map_hash_call" = call i64 @"_map_hash"(i64 %"key_load", i64 %"cap_load")
  %"idx" = alloca i64
  store i64 %"_map_hash_call", i64* %"idx"
  %"idx_load" = load i64, i64* %"idx"
  %"i" = alloca i64
  store i64 %"idx_load", i64* %"i"
  %"probes" = alloca i64
  store i64 0, i64* %"probes"
  br label %"while_cond"
while_cond:
  %"probes_load" = load i64, i64* %"probes"
  %"self_load.1" = load %"Map"*, %"Map"** %"self"
  %".12" = getelementptr %"Map", %"Map"* %"self_load.1", i32 0, i32 3
  %"cap_load.1" = load i64, i64* %".12"
  %"icmp" = icmp slt i64 %"probes_load", %"cap_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"self_load.2" = load %"Map"*, %"Map"** %"self"
  %".14" = getelementptr %"Map", %"Map"* %"self_load.2", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".14"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i64, i64* %"keys_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".15"
  %"k" = alloca i64
  store i64 %"ptr_idx_load", i64* %"k"
  %"k_load" = load i64, i64* %"k"
  %"neg" = sub i64 0, 1
  %"icmp.1" = icmp eq i64 %"k_load", %"neg"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret i64 0
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"k_load.1" = load i64, i64* %"k"
  %"key_load.1" = load i64, i64* %"key"
  %"icmp.2" = icmp eq i64 %"k_load.1", %"key_load.1"
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"neg.1" = sub i64 0, 2
  %"self_load.3" = load %"Map"*, %"Map"** %"self"
  %".21" = getelementptr %"Map", %"Map"* %"self_load.3", i32 0, i32 0
  %"keys_load.1" = load i64*, i64** %".21"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load.1", i64 %"i_load.1"
  store i64 %"neg.1", i64* %"idx_ptr"
  %"self_load.4" = load %"Map"*, %"Map"** %"self"
  %".23" = getelementptr %"Map", %"Map"* %"self_load.4", i32 0, i32 2
  %"size_load" = load i64, i64* %".23"
  %"sub" = sub i64 %"size_load", 1
  %"self_load.5" = load %"Map"*, %"Map"** %"self"
  %"size_ptr" = getelementptr %"Map", %"Map"* %"self_load.5", i32 0, i32 2
  store i64 %"sub", i64* %"size_ptr"
  ret i64 1
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %"self_load.6" = load %"Map"*, %"Map"** %"self"
  %".27" = getelementptr %"Map", %"Map"* %"self_load.6", i32 0, i32 3
  %"cap_load.2" = load i64, i64* %".27"
  %"sub.1" = sub i64 %"cap_load.2", 1
  %"bitand" = and i64 %"add", %"sub.1"
  store i64 %"bitand", i64* %"i"
  %"probes_load.1" = load i64, i64* %"probes"
  %"add.1" = add i64 %"probes_load.1", 1
  store i64 %"add.1", i64* %"probes"
  br label %"while_cond"
}

define %"Map"* @"new_map"()
{
new_map_entry:
  br label %"new_map_body"
new_map_body:
  %"m" = alloca %"Map"*
  %"m_storage_raw" = call i8* @"GC_malloc"(i64 32)
  %"m_storage" = bitcast i8* %"m_storage_raw" to %"Map"*
  store %"Map" {i64* null, i64* null, i64 0, i64 0}, %"Map"* %"m_storage"
  store %"Map"* %"m_storage", %"Map"** %"m"
  %"m_load" = load %"Map"*, %"Map"** %"m"
  %"cap_ptr" = getelementptr %"Map", %"Map"* %"m_load", i32 0, i32 3
  store i64 16, i64* %"cap_ptr"
  %"m_load.1" = load %"Map"*, %"Map"** %"m"
  %"size_ptr" = getelementptr %"Map", %"Map"* %"m_load.1", i32 0, i32 2
  store i64 0, i64* %"size_ptr"
  %"alloc_size" = mul i64 16, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"m_load.2" = load %"Map"*, %"Map"** %"m"
  %"keys_ptr" = getelementptr %"Map", %"Map"* %"m_load.2", i32 0, i32 0
  %"keys_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"keys_bitcast", i64** %"keys_ptr"
  %"alloc_size.1" = mul i64 16, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"m_load.3" = load %"Map"*, %"Map"** %"m"
  %"values_ptr" = getelementptr %"Map", %"Map"* %"m_load.3", i32 0, i32 1
  %"values_bitcast" = bitcast i8* %"alloc_call.1" to i64*
  store i64* %"values_bitcast", i64** %"values_ptr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 16
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"neg" = sub i64 0, 1
  %"m_load.4" = load %"Map"*, %"Map"** %"m"
  %".12" = getelementptr %"Map", %"Map"* %"m_load.4", i32 0, i32 0
  %"keys_load" = load i64*, i64** %".12"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"keys_load", i64 %"i_load.1"
  store i64 %"neg", i64* %"idx_ptr"
  %"m_load.5" = load %"Map"*, %"Map"** %"m"
  %".14" = getelementptr %"Map", %"Map"* %"m_load.5", i32 0, i32 1
  %"values_load" = load i64*, i64** %".14"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr.1" = getelementptr i64, i64* %"values_load", i64 %"i_load.2"
  store i64 0, i64* %"idx_ptr.1"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %"m_load.6" = load %"Map"*, %"Map"** %"m"
  ret %"Map"* %"m_load.6"
}

@"str_0" = constant [26 x i8] c"\f0\9f\9a\80 Testando Hash Map...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [10 x i8] c"Valor 10:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [10 x i8] c"Valor 26:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [10 x i8] c"Valor 42:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [10 x i8] c"Valor 99:\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c"\0a\00"