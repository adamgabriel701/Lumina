; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Vector" = type {i64*, i64, i64}
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
  %".7" = bitcast [42 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"new_vector_call" = call %"Vector"* @"new_vector"()
  %"v" = alloca %"Vector"*
  store %"Vector"* %"new_vector_call", %"Vector"** %"v"
  %"v_load" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load", i64 1)
  %"v_load.1" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.1", i64 2)
  %"v_load.2" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.2", i64 3)
  %"v_load.3" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.3", i64 4)
  %"v_load.4" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.4", i64 5)
  %"v_load.5" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.5", i64 6)
  %"v_load.6" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.6", i64 7)
  %"v_load.7" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.7", i64 8)
  %"v_load.8" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.8", i64 9)
  %"v_load.9" = load %"Vector"*, %"Vector"** %"v"
  call void @"Vector_push"(%"Vector"* %"v_load.9", i64 10)
  %".11" = bitcast [15 x i8]* @"str_3" to i8*
  %".12" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".12", i8* %".11")
  %"v_load.10" = load %"Vector"*, %"Vector"** %"v"
  %".13" = getelementptr %"Vector", %"Vector"* %"v_load.10", i32 0, i32 1
  %"len_load" = load i64, i64* %".13"
  %".14" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"len_load")
  %".16" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [12 x i8]* @"str_8" to i8*
  %".18" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"v_load.11" = load %"Vector"*, %"Vector"** %"v"
  %"Vector_get_call" = call i64 @"Vector_get"(%"Vector"* %"v_load.11", i64 0)
  %".19" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".20", i64 %"Vector_get_call")
  %".21" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [12 x i8]* @"str_13" to i8*
  %".23" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %"v_load.12" = load %"Vector"*, %"Vector"** %"v"
  %"Vector_get_call.1" = call i64 @"Vector_get"(%"Vector"* %"v_load.12", i64 4)
  %".24" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"Vector_get_call.1")
  %".26" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [12 x i8]* @"str_18" to i8*
  %".28" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %"v_load.13" = load %"Vector"*, %"Vector"** %"v"
  %"Vector_get_call.2" = call i64 @"Vector_get"(%"Vector"* %"v_load.13", i64 9)
  %".29" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".30", i64 %"Vector_get_call.2")
  %".31" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define %"Vector"* @"Vector_new"(%"Vector"* %".1")
{
Vector_new_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  br label %"Vector_new_body"
Vector_new_body:
  %"v" = alloca %"Vector"*
  %"v_storage_raw" = call i8* @"GC_malloc"(i64 24)
  %"v_storage" = bitcast i8* %"v_storage_raw" to %"Vector"*
  store %"Vector" {i64* null, i64 0, i64 0}, %"Vector"* %"v_storage"
  store %"Vector"* %"v_storage", %"Vector"** %"v"
  %"Option_lit" = call i8* @"GC_malloc"(i64 16)
  %"Option_cast" = bitcast i8* %"Option_lit" to %"Option"*
  %"tag_ptr" = getelementptr %"Option", %"Option"* %"Option_cast", i32 0, i32 0
  store i32 1, i32* %"tag_ptr"
  %"payload_ptr_0" = getelementptr %"Option", %"Option"* %"Option_cast", i32 0, i32 1
  store i64 0, i64* %"payload_ptr_0"
  %"v_load" = load %"Vector"*, %"Vector"** %"v"
  %"data_ptr" = getelementptr %"Vector", %"Vector"* %"v_load", i32 0, i32 0
  %"data_bitcast" = bitcast %"Option"* %"Option_cast" to i64*
  store i64* %"data_bitcast", i64** %"data_ptr"
  %"v_load.1" = load %"Vector"*, %"Vector"** %"v"
  %"len_ptr" = getelementptr %"Vector", %"Vector"* %"v_load.1", i32 0, i32 1
  store i64 0, i64* %"len_ptr"
  %"v_load.2" = load %"Vector"*, %"Vector"** %"v"
  %"cap_ptr" = getelementptr %"Vector", %"Vector"* %"v_load.2", i32 0, i32 2
  store i64 0, i64* %"cap_ptr"
  %"v_load.3" = load %"Vector"*, %"Vector"** %"v"
  ret %"Vector"* %"v_load.3"
}

define void @"Vector_reserve"(%"Vector"* %".1", i64 %".2")
{
Vector_reserve_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  %"min_cap" = alloca i64
  store i64 %".2", i64* %"min_cap"
  br label %"Vector_reserve_body"
Vector_reserve_body:
  %"min_cap_load" = load i64, i64* %"min_cap"
  %"self_load" = load %"Vector"*, %"Vector"** %"self"
  %".7" = getelementptr %"Vector", %"Vector"* %"self_load", i32 0, i32 2
  %"cap_load" = load i64, i64* %".7"
  %"icmp" = icmp sle i64 %"min_cap_load", %"cap_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  ret void
if_else:
  br label %"if_end"
if_end:
  %"self_load.1" = load %"Vector"*, %"Vector"** %"self"
  %".11" = getelementptr %"Vector", %"Vector"* %"self_load.1", i32 0, i32 2
  %"cap_load.1" = load i64, i64* %".11"
  %"new_cap" = alloca i64
  store i64 %"cap_load.1", i64* %"new_cap"
  %"new_cap_load" = load i64, i64* %"new_cap"
  %"icmp.1" = icmp eq i64 %"new_cap_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  store i64 4, i64* %"new_cap"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  br label %"while_cond"
while_cond:
  %"new_cap_load.1" = load i64, i64* %"new_cap"
  %"min_cap_load.1" = load i64, i64* %"min_cap"
  %"icmp.2" = icmp slt i64 %"new_cap_load.1", %"min_cap_load.1"
  br i1 %"icmp.2", label %"while_body", label %"while_end"
while_body:
  %"new_cap_load.2" = load i64, i64* %"new_cap"
  %"mul" = mul i64 %"new_cap_load.2", 2
  store i64 %"mul", i64* %"new_cap"
  br label %"while_cond"
while_end:
  %"new_cap_load.3" = load i64, i64* %"new_cap"
  %"alloc_size" = mul i64 %"new_cap_load.3", 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"new_data" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"new_data"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond.1"
while_cond.1:
  %"i_load" = load i64, i64* %"i"
  %"self_load.2" = load %"Vector"*, %"Vector"** %"self"
  %".24" = getelementptr %"Vector", %"Vector"* %"self_load.2", i32 0, i32 1
  %"len_load" = load i64, i64* %".24"
  %"icmp.3" = icmp slt i64 %"i_load", %"len_load"
  br i1 %"icmp.3", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"self_load.3" = load %"Vector"*, %"Vector"** %"self"
  %".26" = getelementptr %"Vector", %"Vector"* %"self_load.3", i32 0, i32 0
  %"data_load" = load i64*, i64** %".26"
  %"i_load.1" = load i64, i64* %"i"
  %".27" = getelementptr i64, i64* %"data_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".27"
  %"new_data_load" = load i64*, i64** %"new_data"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"new_data_load", i64 %"i_load.2"
  store i64 %"ptr_idx_load", i64* %"idx_ptr"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond.1"
while_end.1:
  %"new_data_load.1" = load i64*, i64** %"new_data"
  %"self_load.4" = load %"Vector"*, %"Vector"** %"self"
  %"data_ptr" = getelementptr %"Vector", %"Vector"* %"self_load.4", i32 0, i32 0
  store i64* %"new_data_load.1", i64** %"data_ptr"
  %"new_cap_load.4" = load i64, i64* %"new_cap"
  %"self_load.5" = load %"Vector"*, %"Vector"** %"self"
  %"cap_ptr" = getelementptr %"Vector", %"Vector"* %"self_load.5", i32 0, i32 2
  store i64 %"new_cap_load.4", i64* %"cap_ptr"
  ret void
}

define void @"Vector_push"(%"Vector"* %".1", i64 %".2")
{
Vector_push_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  %"value" = alloca i64
  store i64 %".2", i64* %"value"
  br label %"Vector_push_body"
Vector_push_body:
  %"self_load" = load %"Vector"*, %"Vector"** %"self"
  %".7" = getelementptr %"Vector", %"Vector"* %"self_load", i32 0, i32 1
  %"len_load" = load i64, i64* %".7"
  %"self_load.1" = load %"Vector"*, %"Vector"** %"self"
  %".8" = getelementptr %"Vector", %"Vector"* %"self_load.1", i32 0, i32 2
  %"cap_load" = load i64, i64* %".8"
  %"icmp" = icmp sge i64 %"len_load", %"cap_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"Vector"*, %"Vector"** %"self"
  %"self_load.3" = load %"Vector"*, %"Vector"** %"self"
  %".10" = getelementptr %"Vector", %"Vector"* %"self_load.3", i32 0, i32 1
  %"len_load.1" = load i64, i64* %".10"
  %"add" = add i64 %"len_load.1", 1
  call void @"Vector_reserve"(%"Vector"* %"self_load.2", i64 %"add")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"value_load" = load i64, i64* %"value"
  %"self_load.4" = load %"Vector"*, %"Vector"** %"self"
  %".13" = getelementptr %"Vector", %"Vector"* %"self_load.4", i32 0, i32 0
  %"data_load" = load i64*, i64** %".13"
  %"self_load.5" = load %"Vector"*, %"Vector"** %"self"
  %".14" = getelementptr %"Vector", %"Vector"* %"self_load.5", i32 0, i32 1
  %"len_load.2" = load i64, i64* %".14"
  %"idx_ptr" = getelementptr i64, i64* %"data_load", i64 %"len_load.2"
  store i64 %"value_load", i64* %"idx_ptr"
  %"self_load.6" = load %"Vector"*, %"Vector"** %"self"
  %".16" = getelementptr %"Vector", %"Vector"* %"self_load.6", i32 0, i32 1
  %"len_load.3" = load i64, i64* %".16"
  %"add.1" = add i64 %"len_load.3", 1
  %"self_load.7" = load %"Vector"*, %"Vector"** %"self"
  %"len_ptr" = getelementptr %"Vector", %"Vector"* %"self_load.7", i32 0, i32 1
  store i64 %"add.1", i64* %"len_ptr"
  ret void
}

define i64 @"Vector_pop"(%"Vector"* %".1")
{
Vector_pop_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  br label %"Vector_pop_body"
Vector_pop_body:
  %"self_load" = load %"Vector"*, %"Vector"** %"self"
  %".5" = getelementptr %"Vector", %"Vector"* %"self_load", i32 0, i32 1
  %"len_load" = load i64, i64* %".5"
  %"sub" = sub i64 %"len_load", 1
  %"self_load.1" = load %"Vector"*, %"Vector"** %"self"
  %"len_ptr" = getelementptr %"Vector", %"Vector"* %"self_load.1", i32 0, i32 1
  store i64 %"sub", i64* %"len_ptr"
  %"self_load.2" = load %"Vector"*, %"Vector"** %"self"
  %".7" = getelementptr %"Vector", %"Vector"* %"self_load.2", i32 0, i32 0
  %"data_load" = load i64*, i64** %".7"
  %"self_load.3" = load %"Vector"*, %"Vector"** %"self"
  %".8" = getelementptr %"Vector", %"Vector"* %"self_load.3", i32 0, i32 1
  %"len_load.1" = load i64, i64* %".8"
  %".9" = getelementptr i64, i64* %"data_load", i64 %"len_load.1"
  %"ptr_idx_load" = load i64, i64* %".9"
  ret i64 %"ptr_idx_load"
}

define i64 @"Vector_get"(%"Vector"* %".1", i64 %".2")
{
Vector_get_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  %"i" = alloca i64
  store i64 %".2", i64* %"i"
  br label %"Vector_get_body"
Vector_get_body:
  %"self_load" = load %"Vector"*, %"Vector"** %"self"
  %".7" = getelementptr %"Vector", %"Vector"* %"self_load", i32 0, i32 0
  %"data_load" = load i64*, i64** %".7"
  %"i_load" = load i64, i64* %"i"
  %".8" = getelementptr i64, i64* %"data_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".8"
  ret i64 %"ptr_idx_load"
}

define void @"Vector_set"(%"Vector"* %".1", i64 %".2", i64 %".3")
{
Vector_set_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  %"i" = alloca i64
  store i64 %".2", i64* %"i"
  %"value" = alloca i64
  store i64 %".3", i64* %"value"
  br label %"Vector_set_body"
Vector_set_body:
  %"value_load" = load i64, i64* %"value"
  %"self_load" = load %"Vector"*, %"Vector"** %"self"
  %".9" = getelementptr %"Vector", %"Vector"* %"self_load", i32 0, i32 0
  %"data_load" = load i64*, i64** %".9"
  %"i_load" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"data_load", i64 %"i_load"
  store i64 %"value_load", i64* %"idx_ptr"
  ret void
}

define void @"Vector_clear"(%"Vector"* %".1")
{
Vector_clear_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  br label %"Vector_clear_body"
Vector_clear_body:
  %"self_load" = load %"Vector"*, %"Vector"** %"self"
  %"len_ptr" = getelementptr %"Vector", %"Vector"* %"self_load", i32 0, i32 1
  store i64 0, i64* %"len_ptr"
  ret void
}

define i64 @"Vector_is_empty"(%"Vector"* %".1")
{
Vector_is_empty_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  br label %"Vector_is_empty_body"
Vector_is_empty_body:
  %"self_load" = load %"Vector"*, %"Vector"** %"self"
  %".5" = getelementptr %"Vector", %"Vector"* %"self_load", i32 0, i32 1
  %"len_load" = load i64, i64* %".5"
  %"icmp" = icmp eq i64 %"len_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  ret i64 1
if_else:
  br label %"if_end"
if_end:
  ret i64 0
}

define i64 @"Vector_sum"(%"Vector"* %".1")
{
Vector_sum_entry:
  %"self" = alloca %"Vector"*
  store %"Vector"* %".1", %"Vector"** %"self"
  br label %"Vector_sum_body"
Vector_sum_body:
  %"total" = alloca i64
  store i64 0, i64* %"total"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"self_load" = load %"Vector"*, %"Vector"** %"self"
  %".8" = getelementptr %"Vector", %"Vector"* %"self_load", i32 0, i32 1
  %"len_load" = load i64, i64* %".8"
  %"icmp" = icmp slt i64 %"i_load", %"len_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"total_load" = load i64, i64* %"total"
  %"self_load.1" = load %"Vector"*, %"Vector"** %"self"
  %".10" = getelementptr %"Vector", %"Vector"* %"self_load.1", i32 0, i32 0
  %"data_load" = load i64*, i64** %".10"
  %"i_load.1" = load i64, i64* %"i"
  %".11" = getelementptr i64, i64* %"data_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i64, i64* %".11"
  %"add" = add i64 %"total_load", %"ptr_idx_load"
  store i64 %"add", i64* %"total"
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.2", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  %"total_load.1" = load i64, i64* %"total"
  ret i64 %"total_load.1"
}

define %"Vector"* @"new_vector"()
{
new_vector_entry:
  br label %"new_vector_body"
new_vector_body:
  %"v" = alloca %"Vector"*
  %"v_storage_raw" = call i8* @"GC_malloc"(i64 24)
  %"v_storage" = bitcast i8* %"v_storage_raw" to %"Vector"*
  store %"Vector" {i64* null, i64 0, i64 0}, %"Vector"* %"v_storage"
  store %"Vector"* %"v_storage", %"Vector"** %"v"
  %"Option_lit" = call i8* @"GC_malloc"(i64 16)
  %"Option_cast" = bitcast i8* %"Option_lit" to %"Option"*
  %"tag_ptr" = getelementptr %"Option", %"Option"* %"Option_cast", i32 0, i32 0
  store i32 1, i32* %"tag_ptr"
  %"payload_ptr_0" = getelementptr %"Option", %"Option"* %"Option_cast", i32 0, i32 1
  store i64 0, i64* %"payload_ptr_0"
  %"v_load" = load %"Vector"*, %"Vector"** %"v"
  %"data_ptr" = getelementptr %"Vector", %"Vector"* %"v_load", i32 0, i32 0
  %"data_bitcast" = bitcast %"Option"* %"Option_cast" to i64*
  store i64* %"data_bitcast", i64** %"data_ptr"
  %"v_load.1" = load %"Vector"*, %"Vector"** %"v"
  %"len_ptr" = getelementptr %"Vector", %"Vector"* %"v_load.1", i32 0, i32 1
  store i64 0, i64* %"len_ptr"
  %"v_load.2" = load %"Vector"*, %"Vector"** %"v"
  %"cap_ptr" = getelementptr %"Vector", %"Vector"* %"v_load.2", i32 0, i32 2
  store i64 0, i64* %"cap_ptr"
  %"v_load.3" = load %"Vector"*, %"Vector"** %"v"
  ret %"Vector"* %"v_load.3"
}

@"str_0" = constant [42 x i8] c"\f0\9f\9a\80 Testando Array Din\c3\a2mico (Vector)...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [15 x i8] c"Tamanho final:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [12 x i8] c"Elemento 0:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [12 x i8] c"Elemento 4:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [12 x i8] c"Elemento 9:\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c"\0a\00"