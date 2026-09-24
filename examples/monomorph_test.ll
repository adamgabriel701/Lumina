; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Box" = type {i64}
%"Box_int_" = type {i64}
%"Box_float_" = type {double}
%"Box_str_" = type {i8*}
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
  %".7" = bitcast [30 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"b1" = alloca %"Box_int_"*
  %"b1_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"b1_storage" = bitcast i8* %"b1_storage_raw" to %"Box_int_"*
  store %"Box_int_" {i64 0}, %"Box_int_"* %"b1_storage"
  store %"Box_int_"* %"b1_storage", %"Box_int_"** %"b1"
  %"b1_load" = load %"Box_int_"*, %"Box_int_"** %"b1"
  %"value_ptr" = getelementptr %"Box_int_", %"Box_int_"* %"b1_load", i32 0, i32 0
  store i64 42, i64* %"value_ptr"
  %"b2" = alloca %"Box_float_"*
  %"b2_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"b2_storage" = bitcast i8* %"b2_storage_raw" to %"Box_float_"*
  store %"Box_float_" {double              0x0}, %"Box_float_"* %"b2_storage"
  store %"Box_float_"* %"b2_storage", %"Box_float_"** %"b2"
  %"b2_load" = load %"Box_float_"*, %"Box_float_"** %"b2"
  %"value_ptr.1" = getelementptr %"Box_float_", %"Box_float_"* %"b2_load", i32 0, i32 0
  store double 0x40091eb851eb851f, double* %"value_ptr.1"
  %"b3" = alloca %"Box_str_"*
  %"b3_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"b3_storage" = bitcast i8* %"b3_storage_raw" to %"Box_str_"*
  store %"Box_str_" {i8* null}, %"Box_str_"* %"b3_storage"
  store %"Box_str_"* %"b3_storage", %"Box_str_"** %"b3"
  %".18" = bitcast [4 x i8]* @"str_3" to i8*
  %"b3_load" = load %"Box_str_"*, %"Box_str_"** %"b3"
  %"value_ptr.2" = getelementptr %"Box_str_", %"Box_str_"* %"b3_load", i32 0, i32 0
  store i8* %".18", i8** %"value_ptr.2"
  %".20" = bitcast [10 x i8]* @"str_4" to i8*
  %".21" = bitcast [3 x i8]* @"str_5" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".20")
  %"b1_load.1" = load %"Box_int_"*, %"Box_int_"** %"b1"
  %".22" = getelementptr %"Box_int_", %"Box_int_"* %"b1_load.1", i32 0, i32 0
  %"value_load" = load i64, i64* %".22"
  %".23" = bitcast [2 x i8]* @"str_6" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %".24" = bitcast [4 x i8]* @"str_7" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".24", i64 %"value_load")
  %".25" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".25")
  %".26" = bitcast [12 x i8]* @"str_9" to i8*
  %".27" = bitcast [3 x i8]* @"str_10" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".27", i8* %".26")
  %"b2_load.1" = load %"Box_float_"*, %"Box_float_"** %"b2"
  %".28" = getelementptr %"Box_float_", %"Box_float_"* %"b2_load.1", i32 0, i32 0
  %"value_load.1" = load double, double* %".28"
  %".29" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".30", double %"value_load.1")
  %".31" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [10 x i8]* @"str_14" to i8*
  %".33" = bitcast [3 x i8]* @"str_15" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %".32")
  %"b3_load.1" = load %"Box_str_"*, %"Box_str_"** %"b3"
  %".34" = getelementptr %"Box_str_", %"Box_str_"* %"b3_load.1", i32 0, i32 0
  %"value_load.2" = load i8*, i8** %".34"
  %".35" = bitcast [2 x i8]* @"str_16" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".35")
  %".36" = bitcast [3 x i8]* @"str_17" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".36", i8* %"value_load.2")
  %".37" = bitcast [2 x i8]* @"str_18" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".37")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [30 x i8] c"Iniciando Monomorphization...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [4 x i8] c"Ola\00"
@"str_4" = constant [10 x i8] c"Box<int>:\00"
@"str_5" = constant [3 x i8] c"%s\00"
@"str_6" = constant [2 x i8] c" \00"
@"str_7" = constant [4 x i8] c"%ld\00"
@"str_8" = constant [2 x i8] c"\0a\00"
@"str_9" = constant [12 x i8] c"Box<float>:\00"
@"str_10" = constant [3 x i8] c"%s\00"
@"str_11" = constant [2 x i8] c" \00"
@"str_12" = constant [3 x i8] c"%f\00"
@"str_13" = constant [2 x i8] c"\0a\00"
@"str_14" = constant [10 x i8] c"Box<str>:\00"
@"str_15" = constant [3 x i8] c"%s\00"
@"str_16" = constant [2 x i8] c" \00"
@"str_17" = constant [3 x i8] c"%s\00"
@"str_18" = constant [2 x i8] c"\0a\00"