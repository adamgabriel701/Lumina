; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Ponto" = type {i64, i64}
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
  %"p1" = alloca %"Ponto"*
  %"p1_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"p1_storage" = bitcast i8* %"p1_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"p1_storage"
  store %"Ponto"* %"p1_storage", %"Ponto"** %"p1"
  %"p1_load" = load %"Ponto"*, %"Ponto"** %"p1"
  %"x_ptr" = getelementptr %"Ponto", %"Ponto"* %"p1_load", i32 0, i32 0
  store i64 10, i64* %"x_ptr"
  %"p1_load.1" = load %"Ponto"*, %"Ponto"** %"p1"
  %"y_ptr" = getelementptr %"Ponto", %"Ponto"* %"p1_load.1", i32 0, i32 1
  store i64 20, i64* %"y_ptr"
  %"p2" = alloca %"Ponto"*
  %"p2_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"p2_storage" = bitcast i8* %"p2_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"p2_storage"
  store %"Ponto"* %"p2_storage", %"Ponto"** %"p2"
  %"p2_load" = load %"Ponto"*, %"Ponto"** %"p2"
  %"x_ptr.1" = getelementptr %"Ponto", %"Ponto"* %"p2_load", i32 0, i32 0
  store i64 10, i64* %"x_ptr.1"
  %"p2_load.1" = load %"Ponto"*, %"Ponto"** %"p2"
  %"y_ptr.1" = getelementptr %"Ponto", %"Ponto"* %"p2_load.1", i32 0, i32 1
  store i64 20, i64* %"y_ptr.1"
  %"p3" = alloca %"Ponto"*
  %"p3_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"p3_storage" = bitcast i8* %"p3_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"p3_storage"
  store %"Ponto"* %"p3_storage", %"Ponto"** %"p3"
  %"p3_load" = load %"Ponto"*, %"Ponto"** %"p3"
  %"x_ptr.2" = getelementptr %"Ponto", %"Ponto"* %"p3_load", i32 0, i32 0
  store i64 10, i64* %"x_ptr.2"
  %"p3_load.1" = load %"Ponto"*, %"Ponto"** %"p3"
  %"y_ptr.2" = getelementptr %"Ponto", %"Ponto"* %"p3_load.1", i32 0, i32 1
  store i64 99, i64* %"y_ptr.2"
  %".19" = bitcast [28 x i8]* @"str_0" to i8*
  %".20" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %".21" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [10 x i8]* @"str_3" to i8*
  %".23" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %"p1_load.2" = load %"Ponto"*, %"Ponto"** %"p1"
  %"p2_load.2" = load %"Ponto"*, %"Ponto"** %"p2"
  %"op_Ponto___eq__" = call i1 @"Ponto___eq__"(%"Ponto"* %"p1_load.2", %"Ponto"* %"p2_load.2")
  %".24" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [5 x i8]* @"str_6" to i8*
  %".26" = bitcast [6 x i8]* @"str_7" to i8*
  %"print_bool" = select  i1 %"op_Ponto___eq__", i8* %".25", i8* %".26"
  %".27" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".27", i8* %"print_bool")
  %".28" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".28")
  %".29" = bitcast [10 x i8]* @"str_10" to i8*
  %".30" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".29")
  %"p1_load.3" = load %"Ponto"*, %"Ponto"** %"p1"
  %"p3_load.2" = load %"Ponto"*, %"Ponto"** %"p3"
  %"op_Ponto___eq__.1" = call i1 @"Ponto___eq__"(%"Ponto"* %"p1_load.3", %"Ponto"* %"p3_load.2")
  %".31" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [5 x i8]* @"str_13" to i8*
  %".33" = bitcast [6 x i8]* @"str_14" to i8*
  %"print_bool.1" = select  i1 %"op_Ponto___eq__.1", i8* %".32", i8* %".33"
  %".34" = bitcast [3 x i8]* @"str_15" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".34", i8* %"print_bool.1")
  %".35" = bitcast [2 x i8]* @"str_16" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".35")
  %".36" = bitcast [10 x i8]* @"str_17" to i8*
  %".37" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".37", i8* %".36")
  %"p1_load.4" = load %"Ponto"*, %"Ponto"** %"p1"
  %"p2_load.3" = load %"Ponto"*, %"Ponto"** %"p2"
  %"op_Ponto___ne__" = call i1 @"Ponto___ne__"(%"Ponto"* %"p1_load.4", %"Ponto"* %"p2_load.3")
  %".38" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".38")
  %".39" = bitcast [5 x i8]* @"str_20" to i8*
  %".40" = bitcast [6 x i8]* @"str_21" to i8*
  %"print_bool.2" = select  i1 %"op_Ponto___ne__", i8* %".39", i8* %".40"
  %".41" = bitcast [3 x i8]* @"str_22" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".41", i8* %"print_bool.2")
  %".42" = bitcast [2 x i8]* @"str_23" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".42")
  %".43" = bitcast [10 x i8]* @"str_24" to i8*
  %".44" = bitcast [3 x i8]* @"str_25" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".44", i8* %".43")
  %"p1_load.5" = load %"Ponto"*, %"Ponto"** %"p1"
  %"p3_load.3" = load %"Ponto"*, %"Ponto"** %"p3"
  %"op_Ponto___ne__.1" = call i1 @"Ponto___ne__"(%"Ponto"* %"p1_load.5", %"Ponto"* %"p3_load.3")
  %".45" = bitcast [2 x i8]* @"str_26" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".45")
  %".46" = bitcast [5 x i8]* @"str_27" to i8*
  %".47" = bitcast [6 x i8]* @"str_28" to i8*
  %"print_bool.3" = select  i1 %"op_Ponto___ne__.1", i8* %".46", i8* %".47"
  %".48" = bitcast [3 x i8]* @"str_29" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".48", i8* %"print_bool.3")
  %".49" = bitcast [2 x i8]* @"str_30" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".49")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define i1 @"Ponto___eq__"(%"Ponto"* %".1", %"Ponto"* %".2")
{
Ponto___eq___entry:
  %"a" = alloca %"Ponto"*
  store %"Ponto"* %".1", %"Ponto"** %"a"
  %"b" = alloca %"Ponto"*
  store %"Ponto"* %".2", %"Ponto"** %"b"
  br label %"Ponto___eq___body"
Ponto___eq___body:
  %"a_load" = load %"Ponto"*, %"Ponto"** %"a"
  %".7" = getelementptr %"Ponto", %"Ponto"* %"a_load", i32 0, i32 0
  %"x_load" = load i64, i64* %".7"
  %"b_load" = load %"Ponto"*, %"Ponto"** %"b"
  %".8" = getelementptr %"Ponto", %"Ponto"* %"b_load", i32 0, i32 0
  %"x_load.1" = load i64, i64* %".8"
  %"icmp" = icmp eq i64 %"x_load", %"x_load.1"
  br i1 %"icmp", label %"and_rhs", label %"and_end"
and_rhs:
  %"a_load.1" = load %"Ponto"*, %"Ponto"** %"a"
  %".10" = getelementptr %"Ponto", %"Ponto"* %"a_load.1", i32 0, i32 1
  %"y_load" = load i64, i64* %".10"
  %"b_load.1" = load %"Ponto"*, %"Ponto"** %"b"
  %".11" = getelementptr %"Ponto", %"Ponto"* %"b_load.1", i32 0, i32 1
  %"y_load.1" = load i64, i64* %".11"
  %"icmp.1" = icmp eq i64 %"y_load", %"y_load.1"
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"Ponto___eq___body"], [%"icmp.1", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  ret i1 1
if_else:
  br label %"if_end"
if_end:
  ret i1 0
}

define i1 @"Ponto___ne__"(%"Ponto"* %".1", %"Ponto"* %".2")
{
Ponto___ne___entry:
  %"a" = alloca %"Ponto"*
  store %"Ponto"* %".1", %"Ponto"** %"a"
  %"b" = alloca %"Ponto"*
  store %"Ponto"* %".2", %"Ponto"** %"b"
  br label %"Ponto___ne___body"
Ponto___ne___body:
  %"a_load" = load %"Ponto"*, %"Ponto"** %"a"
  %"b_load" = load %"Ponto"*, %"Ponto"** %"b"
  %"Ponto___eq___call" = call i1 @"Ponto___eq__"(%"Ponto"* %"a_load", %"Ponto"* %"b_load")
  %"not_bool" = xor i1 %"Ponto___eq___call", 1
  br i1 %"not_bool", label %"if_then", label %"if_else"
if_then:
  ret i1 1
if_else:
  br label %"if_end"
if_end:
  ret i1 0
}

@"str_0" = constant [28 x i8] c"=== PartialEq (== e !=) ===\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [10 x i8] c"p1 == p2?\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [5 x i8] c"true\00"
@"str_7" = constant [6 x i8] c"false\00"
@"str_8" = constant [3 x i8] c"%s\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [10 x i8] c"p1 == p3?\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c" \00"
@"str_13" = constant [5 x i8] c"true\00"
@"str_14" = constant [6 x i8] c"false\00"
@"str_15" = constant [3 x i8] c"%s\00"
@"str_16" = constant [2 x i8] c"\0a\00"
@"str_17" = constant [10 x i8] c"p1 != p2?\00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c" \00"
@"str_20" = constant [5 x i8] c"true\00"
@"str_21" = constant [6 x i8] c"false\00"
@"str_22" = constant [3 x i8] c"%s\00"
@"str_23" = constant [2 x i8] c"\0a\00"
@"str_24" = constant [10 x i8] c"p1 != p3?\00"
@"str_25" = constant [3 x i8] c"%s\00"
@"str_26" = constant [2 x i8] c" \00"
@"str_27" = constant [5 x i8] c"true\00"
@"str_28" = constant [6 x i8] c"false\00"
@"str_29" = constant [3 x i8] c"%s\00"
@"str_30" = constant [2 x i8] c"\0a\00"