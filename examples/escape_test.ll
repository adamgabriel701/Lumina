; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
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
define i64* @"criar_array_global"()
{
criar_array_global_entry:
  br label %"criar_array_global_body"
criar_array_global_body:
  %"alloc_size" = mul i64 3, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"arr" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"arr"
  %"arr_load" = load i64*, i64** %"arr"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load", i64 0
  store i64 10, i64* %"idx_ptr"
  %"arr_load.1" = load i64*, i64** %"arr"
  %"idx_ptr.1" = getelementptr i64, i64* %"arr_load.1", i64 1
  store i64 20, i64* %"idx_ptr.1"
  %"arr_load.2" = load i64*, i64** %"arr"
  %"idx_ptr.2" = getelementptr i64, i64* %"arr_load.2", i64 2
  store i64 30, i64* %"idx_ptr.2"
  %"arr_load.3" = load i64*, i64** %"arr"
  ret i64* %"arr_load.3"
}

define void @"processar_local"()
{
processar_local_entry:
  br label %"processar_local_body"
processar_local_body:
  %"alloc_size" = mul i64 3, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"arr" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"arr"
  %"arr_load" = load i64*, i64** %"arr"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load", i64 0
  store i64 100, i64* %"idx_ptr"
  %"arr_load.1" = load i64*, i64** %"arr"
  %"idx_ptr.1" = getelementptr i64, i64* %"arr_load.1", i64 1
  store i64 200, i64* %"idx_ptr.1"
  %"arr_load.2" = load i64*, i64** %"arr"
  %"idx_ptr.2" = getelementptr i64, i64* %"arr_load.2", i64 2
  store i64 300, i64* %"idx_ptr.2"
  %".7" = bitcast [22 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %"arr_load.3" = load i64*, i64** %"arr"
  %".9" = getelementptr i64, i64* %"arr_load.3", i64 0
  %"ptr_idx_load" = load i64, i64* %".9"
  %".10" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %".11" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".11", i64 %"ptr_idx_load")
  %"arr_load.4" = load i64*, i64** %"arr"
  %".12" = getelementptr i64, i64* %"arr_load.4", i64 1
  %"ptr_idx_load.1" = load i64, i64* %".12"
  %".13" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".13")
  %".14" = bitcast [4 x i8]* @"str_5" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".14", i64 %"ptr_idx_load.1")
  %"arr_load.5" = load i64*, i64** %"arr"
  %".15" = getelementptr i64, i64* %"arr_load.5", i64 2
  %"ptr_idx_load.2" = load i64, i64* %".15"
  %".16" = bitcast [2 x i8]* @"str_6" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [4 x i8]* @"str_7" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".17", i64 %"ptr_idx_load.2")
  %".18" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".18")
  ret void
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  call void @"processar_local"()
  %"criar_array_global_call" = call i64* @"criar_array_global"()
  %"global_arr" = alloca i64*
  store i64* %"criar_array_global_call", i64** %"global_arr"
  %".8" = bitcast [22 x i8]* @"str_9" to i8*
  %".9" = bitcast [3 x i8]* @"str_10" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".9", i8* %".8")
  %"global_arr_load" = load i64*, i64** %"global_arr"
  %".10" = getelementptr i64, i64* %"global_arr_load", i64 0
  %"ptr_idx_load" = load i64, i64* %".10"
  %".11" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".11")
  %".12" = bitcast [4 x i8]* @"str_12" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".12", i64 %"ptr_idx_load")
  %"global_arr_load.1" = load i64*, i64** %"global_arr"
  %".13" = getelementptr i64, i64* %"global_arr_load.1", i64 1
  %"ptr_idx_load.1" = load i64, i64* %".13"
  %".14" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [4 x i8]* @"str_14" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"ptr_idx_load.1")
  %"global_arr_load.2" = load i64*, i64** %"global_arr"
  %".16" = getelementptr i64, i64* %"global_arr_load.2", i64 2
  %"ptr_idx_load.2" = load i64, i64* %".16"
  %".17" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i64 %"ptr_idx_load.2")
  %".19" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [22 x i8] c"Array local na Stack:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c" \00"
@"str_5" = constant [4 x i8] c"%ld\00"
@"str_6" = constant [2 x i8] c" \00"
@"str_7" = constant [4 x i8] c"%ld\00"
@"str_8" = constant [2 x i8] c"\0a\00"
@"str_9" = constant [22 x i8] c"Array global no Heap:\00"
@"str_10" = constant [3 x i8] c"%s\00"
@"str_11" = constant [2 x i8] c" \00"
@"str_12" = constant [4 x i8] c"%ld\00"
@"str_13" = constant [2 x i8] c" \00"
@"str_14" = constant [4 x i8] c"%ld\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"