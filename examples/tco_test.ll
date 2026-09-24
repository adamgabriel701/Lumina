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
define i64 @"sum_rec"(i64 %".1", i64 %".2")
{
sum_rec_entry:
  %"n" = alloca i64
  store i64 %".1", i64* %"n"
  %"acc" = alloca i64
  store i64 %".2", i64* %"acc"
  br label %"sum_rec_body"
sum_rec_body:
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp eq i64 %"n_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"acc_load" = load i64, i64* %"acc"
  ret i64 %"acc_load"
if_else:
  br label %"if_end"
if_end:
  %"n_load.1" = load i64, i64* %"n"
  %"sub" = sub i64 %"n_load.1", 1
  %"acc_load.1" = load i64, i64* %"acc"
  %"n_load.2" = load i64, i64* %"n"
  %"add" = add i64 %"acc_load.1", %"n_load.2"
  store i64 %"sub", i64* %"n"
  store i64 %"add", i64* %"acc"
  br label %"sum_rec_body"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [34 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"sum_rec_call" = call i64 @"sum_rec"(i64 1000000, i64 0)
  %"res" = alloca i64
  store i64 %"sum_rec_call", i64* %"res"
  %".11" = bitcast [16 x i8]* @"str_3" to i8*
  %".12" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".12", i8* %".11")
  %"res_load" = load i64, i64* %"res"
  %".13" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".13")
  %".14" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".14", i64 %"res_load")
  %".15" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [34 x i8] c"Iniciando TCO Test (N=1000000)...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [16 x i8] c"Soma 1 at\c3\a9 1M:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"