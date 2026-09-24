; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Vector2" = type {i64, i64}
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
define %"Vector2"* @"Vector2___add__"(%"Vector2"* %".1", %"Vector2"* %".2")
{
Vector2___add___entry:
  %"a" = alloca %"Vector2"*
  store %"Vector2"* %".1", %"Vector2"** %"a"
  %"b" = alloca %"Vector2"*
  store %"Vector2"* %".2", %"Vector2"** %"b"
  br label %"Vector2___add___body"
Vector2___add___body:
  %"result" = alloca %"Vector2"*
  %"result_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"result_storage" = bitcast i8* %"result_storage_raw" to %"Vector2"*
  store %"Vector2" {i64 0, i64 0}, %"Vector2"* %"result_storage"
  store %"Vector2"* %"result_storage", %"Vector2"** %"result"
  %"a_load" = load %"Vector2"*, %"Vector2"** %"a"
  %".9" = getelementptr %"Vector2", %"Vector2"* %"a_load", i32 0, i32 0
  %"x_load" = load i64, i64* %".9"
  %"b_load" = load %"Vector2"*, %"Vector2"** %"b"
  %".10" = getelementptr %"Vector2", %"Vector2"* %"b_load", i32 0, i32 0
  %"x_load.1" = load i64, i64* %".10"
  %"add" = add i64 %"x_load", %"x_load.1"
  %"result_load" = load %"Vector2"*, %"Vector2"** %"result"
  %"x_ptr" = getelementptr %"Vector2", %"Vector2"* %"result_load", i32 0, i32 0
  store i64 %"add", i64* %"x_ptr"
  %"a_load.1" = load %"Vector2"*, %"Vector2"** %"a"
  %".12" = getelementptr %"Vector2", %"Vector2"* %"a_load.1", i32 0, i32 1
  %"y_load" = load i64, i64* %".12"
  %"b_load.1" = load %"Vector2"*, %"Vector2"** %"b"
  %".13" = getelementptr %"Vector2", %"Vector2"* %"b_load.1", i32 0, i32 1
  %"y_load.1" = load i64, i64* %".13"
  %"add.1" = add i64 %"y_load", %"y_load.1"
  %"result_load.1" = load %"Vector2"*, %"Vector2"** %"result"
  %"y_ptr" = getelementptr %"Vector2", %"Vector2"* %"result_load.1", i32 0, i32 1
  store i64 %"add.1", i64* %"y_ptr"
  %"result_load.2" = load %"Vector2"*, %"Vector2"** %"result"
  ret %"Vector2"* %"result_load.2"
}

define i64 @"Vector2___eq__"(%"Vector2"* %".1", %"Vector2"* %".2")
{
Vector2___eq___entry:
  %"a" = alloca %"Vector2"*
  store %"Vector2"* %".1", %"Vector2"** %"a"
  %"b" = alloca %"Vector2"*
  store %"Vector2"* %".2", %"Vector2"** %"b"
  br label %"Vector2___eq___body"
Vector2___eq___body:
  %"a_load" = load %"Vector2"*, %"Vector2"** %"a"
  %".7" = getelementptr %"Vector2", %"Vector2"* %"a_load", i32 0, i32 0
  %"x_load" = load i64, i64* %".7"
  %"b_load" = load %"Vector2"*, %"Vector2"** %"b"
  %".8" = getelementptr %"Vector2", %"Vector2"* %"b_load", i32 0, i32 0
  %"x_load.1" = load i64, i64* %".8"
  %"icmp" = icmp eq i64 %"x_load", %"x_load.1"
  br i1 %"icmp", label %"and_rhs", label %"and_end"
and_rhs:
  %"a_load.1" = load %"Vector2"*, %"Vector2"** %"a"
  %".10" = getelementptr %"Vector2", %"Vector2"* %"a_load.1", i32 0, i32 1
  %"y_load" = load i64, i64* %".10"
  %"b_load.1" = load %"Vector2"*, %"Vector2"** %"b"
  %".11" = getelementptr %"Vector2", %"Vector2"* %"b_load.1", i32 0, i32 1
  %"y_load.1" = load i64, i64* %".11"
  %"icmp.1" = icmp eq i64 %"y_load", %"y_load.1"
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"Vector2___eq___body"], [%"icmp.1", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  ret i64 1
if_else:
  br label %"if_end"
if_end:
  ret i64 0
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [33 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"v1" = alloca %"Vector2"*
  %"v1_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"v1_storage" = bitcast i8* %"v1_storage_raw" to %"Vector2"*
  store %"Vector2" {i64 0, i64 0}, %"Vector2"* %"v1_storage"
  store %"Vector2"* %"v1_storage", %"Vector2"** %"v1"
  %"v1_load" = load %"Vector2"*, %"Vector2"** %"v1"
  %"x_ptr" = getelementptr %"Vector2", %"Vector2"* %"v1_load", i32 0, i32 0
  store i64 10, i64* %"x_ptr"
  %"v1_load.1" = load %"Vector2"*, %"Vector2"** %"v1"
  %"y_ptr" = getelementptr %"Vector2", %"Vector2"* %"v1_load.1", i32 0, i32 1
  store i64 20, i64* %"y_ptr"
  %"v2" = alloca %"Vector2"*
  %"v2_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"v2_storage" = bitcast i8* %"v2_storage_raw" to %"Vector2"*
  store %"Vector2" {i64 0, i64 0}, %"Vector2"* %"v2_storage"
  store %"Vector2"* %"v2_storage", %"Vector2"** %"v2"
  %"v2_load" = load %"Vector2"*, %"Vector2"** %"v2"
  %"x_ptr.1" = getelementptr %"Vector2", %"Vector2"* %"v2_load", i32 0, i32 0
  store i64 5, i64* %"x_ptr.1"
  %"v2_load.1" = load %"Vector2"*, %"Vector2"** %"v2"
  %"y_ptr.1" = getelementptr %"Vector2", %"Vector2"* %"v2_load.1", i32 0, i32 1
  store i64 5, i64* %"y_ptr.1"
  %"v1_load.2" = load %"Vector2"*, %"Vector2"** %"v1"
  %"v2_load.2" = load %"Vector2"*, %"Vector2"** %"v2"
  %"op_Vector2___add__" = call %"Vector2"* @"Vector2___add__"(%"Vector2"* %"v1_load.2", %"Vector2"* %"v2_load.2")
  %"op_Vector2___add___copy" = alloca %"Vector2"
  %"op_src_0" = getelementptr %"Vector2", %"Vector2"* %"op_Vector2___add__", i32 0, i32 0
  %"op_dst_0" = getelementptr %"Vector2", %"Vector2"* %"op_Vector2___add___copy", i32 0, i32 0
  %"op_field_0" = load i64, i64* %"op_src_0"
  store i64 %"op_field_0", i64* %"op_dst_0"
  %"op_src_1" = getelementptr %"Vector2", %"Vector2"* %"op_Vector2___add__", i32 0, i32 1
  %"op_dst_1" = getelementptr %"Vector2", %"Vector2"* %"op_Vector2___add___copy", i32 0, i32 1
  %"op_field_1" = load i64, i64* %"op_src_1"
  store i64 %"op_field_1", i64* %"op_dst_1"
  %"v3" = alloca %"Vector2"*
  store %"Vector2"* %"op_Vector2___add___copy", %"Vector2"** %"v3"
  %".21" = bitcast [6 x i8]* @"str_3" to i8*
  %".22" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".22", i8* %".21")
  %"v3_load" = load %"Vector2"*, %"Vector2"** %"v3"
  %".23" = getelementptr %"Vector2", %"Vector2"* %"v3_load", i32 0, i32 0
  %"x_load" = load i64, i64* %".23"
  %".24" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"x_load")
  %".26" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [6 x i8]* @"str_8" to i8*
  %".28" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %"v3_load.1" = load %"Vector2"*, %"Vector2"** %"v3"
  %".29" = getelementptr %"Vector2", %"Vector2"* %"v3_load.1", i32 0, i32 1
  %"y_load" = load i64, i64* %".29"
  %".30" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %".31" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".31", i64 %"y_load")
  %".32" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".32")
  %"v1_load.3" = load %"Vector2"*, %"Vector2"** %"v1"
  %"v2_load.3" = load %"Vector2"*, %"Vector2"** %"v2"
  %"op_Vector2___eq__" = call i64 @"Vector2___eq__"(%"Vector2"* %"v1_load.3", %"Vector2"* %"v2_load.3")
  %"iguais" = alloca i1
  %"trunc_cast" = trunc i64 %"op_Vector2___eq__" to i1
  store i1 %"trunc_cast", i1* %"iguais"
  %".34" = bitcast [18 x i8]* @"str_13" to i8*
  %".35" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".35", i8* %".34")
  %"iguais_load" = load i1, i1* %"iguais"
  %".36" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %".37" = bitcast [5 x i8]* @"str_16" to i8*
  %".38" = bitcast [6 x i8]* @"str_17" to i8*
  %"print_bool" = select  i1 %"iguais_load", i8* %".37", i8* %".38"
  %".39" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".39", i8* %"print_bool")
  %".40" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".40")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [33 x i8] c"Testando Operator Overloading...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [6 x i8] c"V3 X:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [6 x i8] c"V3 Y:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [18 x i8] c"V1 \c3\a9 igual a V2?\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [5 x i8] c"true\00"
@"str_17" = constant [6 x i8] c"false\00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c"\0a\00"