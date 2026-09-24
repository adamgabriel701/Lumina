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
define void @"greet"(i8* %".1", i64 %".2")
{
greet_entry:
  %"name" = alloca i8*
  store i8* %".1", i8** %"name"
  %"times" = alloca i64
  store i64 %".2", i64* %"times"
  br label %"greet_body"
greet_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"times_load" = load i64, i64* %"times"
  %"icmp" = icmp slt i64 %"i_load", %"times_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %".10" = bitcast [8 x i8]* @"str_0" to i8*
  %"name_load" = load i8*, i8** %"name"
  %"sconcat_len1" = call i64 @"strlen"(i8* %".10")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"name_load")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".10")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"name_load")
  %".11" = bitcast [2 x i8]* @"str_1" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".11")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".11")
  %"msg" = alloca i8*
  store i8* %"sconcat_buf.1", i8** %"msg"
  %"msg_load" = load i8*, i8** %"msg"
  %".13" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %"msg_load")
  %".14" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %"i_load.1" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.1", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
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
  %".7" = bitcast [32 x i8]* @"str_4" to i8*
  %".8" = bitcast [3 x i8]* @"str_5" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_6" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %".10" = bitcast [6 x i8]* @"str_7" to i8*
  call void @"greet"(i8* %".10", i64 1)
  %".11" = bitcast [7 x i8]* @"str_8" to i8*
  call void @"greet"(i8* %".11", i64 1)
  %".12" = bitcast [9 x i8]* @"str_9" to i8*
  call void @"greet"(i8* %".12", i64 3)
  %".13" = bitcast [1 x i8]* @"str_10" to i8*
  %".14" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %".15" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [26 x i8]* @"str_13" to i8*
  %".17" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".17", i8* %".16")
  %".18" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %"x" = alloca i64
  store i64 5, i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"if_cond" = icmp ne i64 0, 0
  br i1 %"if_cond", label %"if_then", label %"if_else"
if_then:
  %".21" = bitcast [22 x i8]* @"str_16" to i8*
  %".22" = bitcast [3 x i8]* @"str_17" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".22", i8* %".21")
  %".23" = bitcast [2 x i8]* @"str_18" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".23")
  br label %"if_end"
if_else:
  %".25" = bitcast [23 x i8]* @"str_19" to i8*
  %".26" = bitcast [3 x i8]* @"str_20" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".26", i8* %".25")
  %".27" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".27")
  br label %"if_end"
if_end:
  %"y" = alloca i64
  store i64 50, i64* %"y"
  %"y_load" = load i64, i64* %"y"
  %"if_cond.1" = icmp ne i64 0, 0
  br i1 %"if_cond.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %".31" = bitcast [22 x i8]* @"str_22" to i8*
  %".32" = bitcast [3 x i8]* @"str_23" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".32", i8* %".31")
  %".33" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".33")
  br label %"if_end.1"
if_else.1:
  %".35" = bitcast [23 x i8]* @"str_25" to i8*
  %".36" = bitcast [3 x i8]* @"str_26" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".36", i8* %".35")
  %".37" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".37")
  br label %"if_end.1"
if_end.1:
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [8 x i8] c"Hello, \00"
@"str_1" = constant [2 x i8] c"!\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c"\0a\00"
@"str_4" = constant [32 x i8] c"Testando Par\c3\a2metros Padr\c3\a3o...\00"
@"str_5" = constant [3 x i8] c"%s\00"
@"str_6" = constant [2 x i8] c"\0a\00"
@"str_7" = constant [6 x i8] c"World\00"
@"str_8" = constant [7 x i8] c"Lumina\00"
@"str_9" = constant [9 x i8] c"Sistemas\00"
@"str_10" = constant [1 x i8] c"\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [26 x i8] c"Testando Operador 'in'...\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c"\0a\00"
@"str_16" = constant [22 x i8] c"X est\c3\a1 entre 0 e 10!\00"
@"str_17" = constant [3 x i8] c"%s\00"
@"str_18" = constant [2 x i8] c"\0a\00"
@"str_19" = constant [23 x i8] c"X est\c3\a1 fora do range.\00"
@"str_20" = constant [3 x i8] c"%s\00"
@"str_21" = constant [2 x i8] c"\0a\00"
@"str_22" = constant [22 x i8] c"Y est\c3\a1 entre 0 e 10!\00"
@"str_23" = constant [3 x i8] c"%s\00"
@"str_24" = constant [2 x i8] c"\0a\00"
@"str_25" = constant [23 x i8] c"Y est\c3\a1 fora do range.\00"
@"str_26" = constant [3 x i8] c"%s\00"
@"str_27" = constant [2 x i8] c"\0a\00"