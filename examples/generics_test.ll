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
  %".7" = bitcast [24 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"identidade__int_call" = call i64 @"identidade__int"(i64 42)
  %"a" = alloca i64
  store i64 %"identidade__int_call", i64* %"a"
  %"a_load" = load i64, i64* %"a"
  %".11" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".11", i64 %"a_load")
  %".12" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %".13" = bitcast [26 x i8]* @"str_5" to i8*
  %".14" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %".15" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %"identidade__float_call" = call double @"identidade__float"(double 0x40091eb851eb851f)
  %"b" = alloca double
  store double %"identidade__float_call", double* %"b"
  %"b_load" = load double, double* %"b"
  %".17" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".17", double %"b_load")
  %".18" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %".19" = bitcast [29 x i8]* @"str_10" to i8*
  %".20" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %".21" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %"box_i" = alloca %"Box_int_"*
  %"box_i_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"box_i_storage" = bitcast i8* %"box_i_storage_raw" to %"Box_int_"*
  store %"Box_int_" {i64 0}, %"Box_int_"* %"box_i_storage"
  store %"Box_int_"* %"box_i_storage", %"Box_int_"** %"box_i"
  %"box_i_load" = load %"Box_int_"*, %"Box_int_"** %"box_i"
  call void @"put__int"(%"Box_int_"* %"box_i_load", i64 100)
  %"box_i_load.1" = load %"Box_int_"*, %"Box_int_"** %"box_i"
  %"get__int_call" = call i64 @"get__int"(%"Box_int_"* %"box_i_load.1")
  %"v_i" = alloca i64
  store i64 %"get__int_call", i64* %"v_i"
  %".25" = bitcast [7 x i8]* @"str_13" to i8*
  %".26" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".26", i8* %".25")
  %"v_i_load" = load i64, i64* %"v_i"
  %".27" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".27")
  %".28" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".28", i64 %"v_i_load")
  %".29" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [31 x i8]* @"str_18" to i8*
  %".31" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".31", i8* %".30")
  %".32" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".32")
  %"box_f" = alloca %"Box_float_"*
  %"box_f_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"box_f_storage" = bitcast i8* %"box_f_storage_raw" to %"Box_float_"*
  store %"Box_float_" {double              0x0}, %"Box_float_"* %"box_f_storage"
  store %"Box_float_"* %"box_f_storage", %"Box_float_"** %"box_f"
  %"box_f_load" = load %"Box_float_"*, %"Box_float_"** %"box_f"
  call void @"put__float"(%"Box_float_"* %"box_f_load", double 0x4005ae147ae147ae)
  %"box_f_load.1" = load %"Box_float_"*, %"Box_float_"** %"box_f"
  %"get__float_call" = call double @"get__float"(%"Box_float_"* %"box_f_load.1")
  %"v_f" = alloca i64
  %"float_to_int_store" = fptosi double %"get__float_call" to i64
  store i64 %"float_to_int_store", i64* %"v_f"
  %".36" = bitcast [7 x i8]* @"str_21" to i8*
  %".37" = bitcast [3 x i8]* @"str_22" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".37", i8* %".36")
  %"v_f_load" = load i64, i64* %"v_f"
  %".38" = bitcast [2 x i8]* @"str_23" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".38")
  %".39" = bitcast [4 x i8]* @"str_24" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".39", i64 %"v_f_load")
  %".40" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_nl.7" = call i32 (i8*, ...) @"printf"(i8* %".40")
  %".41" = bitcast [29 x i8]* @"str_26" to i8*
  %".42" = bitcast [3 x i8]* @"str_27" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".42", i8* %".41")
  %".43" = bitcast [2 x i8]* @"str_28" to i8*
  %"print_nl.8" = call i32 (i8*, ...) @"printf"(i8* %".43")
  %"box_s" = alloca %"Box_str_"*
  %"box_s_storage_raw" = call i8* @"GC_malloc"(i64 8)
  %"box_s_storage" = bitcast i8* %"box_s_storage_raw" to %"Box_str_"*
  store %"Box_str_" {i8* null}, %"Box_str_"* %"box_s_storage"
  store %"Box_str_"* %"box_s_storage", %"Box_str_"** %"box_s"
  %"box_s_load" = load %"Box_str_"*, %"Box_str_"** %"box_s"
  %".46" = bitcast [7 x i8]* @"str_29" to i8*
  call void @"put__str"(%"Box_str_"* %"box_s_load", i8* %".46")
  %"box_s_load.1" = load %"Box_str_"*, %"Box_str_"** %"box_s"
  %"get__str_call" = call i8* @"get__str"(%"Box_str_"* %"box_s_load.1")
  %"v_s" = alloca i64
  %"str_to_int_call" = call i64 @"atoi"(i8* %"get__str_call")
  store i64 %"str_to_int_call", i64* %"v_s"
  %".48" = bitcast [7 x i8]* @"str_30" to i8*
  %".49" = bitcast [3 x i8]* @"str_31" to i8*
  %"print_call.11" = call i32 (i8*, ...) @"printf"(i8* %".49", i8* %".48")
  %"v_s_load" = load i64, i64* %"v_s"
  %".50" = bitcast [2 x i8]* @"str_32" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".50")
  %".51" = bitcast [4 x i8]* @"str_33" to i8*
  %"print_call.12" = call i32 (i8*, ...) @"printf"(i8* %".51", i64 %"v_s_load")
  %".52" = bitcast [2 x i8]* @"str_34" to i8*
  %"print_nl.9" = call i32 (i8*, ...) @"printf"(i8* %".52")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [24 x i8] c"=== identidade<int> ===\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
define i64 @"identidade__int"(i64 %".1")
{
identidade__int_entry:
  %"x" = alloca i64
  store i64 %".1", i64* %"x"
  br label %"identidade__int_body"
identidade__int_body:
  %"x_load" = load i64, i64* %"x"
  ret i64 %"x_load"
}

@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [26 x i8] c"=== identidade<float> ===\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c"\0a\00"
define double @"identidade__float"(double %".1")
{
identidade__float_entry:
  %"x" = alloca double
  store double %".1", double* %"x"
  br label %"identidade__float_body"
identidade__float_body:
  %"x_load" = load double, double* %"x"
  ret double %"x_load"
}

@"str_8" = constant [3 x i8] c"%f\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [29 x i8] c"=== Box<int> com put/get ===\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c"\0a\00"
define void @"put__int"(%"Box_int_"* %".1", i64 %".2")
{
put__int_entry:
  %"b" = alloca %"Box_int_"*
  store %"Box_int_"* %".1", %"Box_int_"** %"b"
  %"val" = alloca i64
  store i64 %".2", i64* %"val"
  br label %"put__int_body"
put__int_body:
  %"val_load" = load i64, i64* %"val"
  %"b_load" = load %"Box_int_"*, %"Box_int_"** %"b"
  %"data_ptr" = getelementptr %"Box_int_", %"Box_int_"* %"b_load", i32 0, i32 0
  store i64 %"val_load", i64* %"data_ptr"
  ret void
}

define i64 @"get__int"(%"Box_int_"* %".1")
{
get__int_entry:
  %"b" = alloca %"Box_int_"*
  store %"Box_int_"* %".1", %"Box_int_"** %"b"
  br label %"get__int_body"
get__int_body:
  %"b_load" = load %"Box_int_"*, %"Box_int_"** %"b"
  %".5" = getelementptr %"Box_int_", %"Box_int_"* %"b_load", i32 0, i32 0
  %"data_load" = load i64, i64* %".5"
  ret i64 %"data_load"
}

@"str_13" = constant [7 x i8] c"valor:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [31 x i8] c"=== Box<float> com put/get ===\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c"\0a\00"
define void @"put__float"(%"Box_float_"* %".1", double %".2")
{
put__float_entry:
  %"b" = alloca %"Box_float_"*
  store %"Box_float_"* %".1", %"Box_float_"** %"b"
  %"val" = alloca double
  store double %".2", double* %"val"
  br label %"put__float_body"
put__float_body:
  %"val_load" = load double, double* %"val"
  %"b_load" = load %"Box_float_"*, %"Box_float_"** %"b"
  %"data_ptr" = getelementptr %"Box_float_", %"Box_float_"* %"b_load", i32 0, i32 0
  store double %"val_load", double* %"data_ptr"
  ret void
}

define double @"get__float"(%"Box_float_"* %".1")
{
get__float_entry:
  %"b" = alloca %"Box_float_"*
  store %"Box_float_"* %".1", %"Box_float_"** %"b"
  br label %"get__float_body"
get__float_body:
  %"b_load" = load %"Box_float_"*, %"Box_float_"** %"b"
  %".5" = getelementptr %"Box_float_", %"Box_float_"* %"b_load", i32 0, i32 0
  %"data_load" = load double, double* %".5"
  ret double %"data_load"
}

@"str_21" = constant [7 x i8] c"valor:\00"
@"str_22" = constant [3 x i8] c"%s\00"
@"str_23" = constant [2 x i8] c" \00"
@"str_24" = constant [4 x i8] c"%ld\00"
@"str_25" = constant [2 x i8] c"\0a\00"
@"str_26" = constant [29 x i8] c"=== Box<str> com put/get ===\00"
@"str_27" = constant [3 x i8] c"%s\00"
@"str_28" = constant [2 x i8] c"\0a\00"
define void @"put__str"(%"Box_str_"* %".1", i8* %".2")
{
put__str_entry:
  %"b" = alloca %"Box_str_"*
  store %"Box_str_"* %".1", %"Box_str_"** %"b"
  %"val" = alloca i8*
  store i8* %".2", i8** %"val"
  br label %"put__str_body"
put__str_body:
  %"val_load" = load i8*, i8** %"val"
  %"b_load" = load %"Box_str_"*, %"Box_str_"** %"b"
  %"data_ptr" = getelementptr %"Box_str_", %"Box_str_"* %"b_load", i32 0, i32 0
  store i8* %"val_load", i8** %"data_ptr"
  ret void
}

@"str_29" = constant [7 x i8] c"Lumina\00"
define i8* @"get__str"(%"Box_str_"* %".1")
{
get__str_entry:
  %"b" = alloca %"Box_str_"*
  store %"Box_str_"* %".1", %"Box_str_"** %"b"
  br label %"get__str_body"
get__str_body:
  %"b_load" = load %"Box_str_"*, %"Box_str_"** %"b"
  %".5" = getelementptr %"Box_str_", %"Box_str_"* %"b_load", i32 0, i32 0
  %"data_load" = load i8*, i8** %".5"
  ret i8* %"data_load"
}

@"str_30" = constant [7 x i8] c"valor:\00"
@"str_31" = constant [3 x i8] c"%s\00"
@"str_32" = constant [2 x i8] c" \00"
@"str_33" = constant [4 x i8] c"%ld\00"
@"str_34" = constant [2 x i8] c"\0a\00"