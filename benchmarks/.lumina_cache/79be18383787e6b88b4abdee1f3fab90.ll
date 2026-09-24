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
declare i64 @"clock"()

define i64 @"main"()
{
main_entry:
  call void @"GC_init"()
  br label %"main_body"
main_body:
  %"clock_call" = call i64 @"clock"()
  %"t" = alloca i64
  store i64 %"clock_call", i64* %"t"
  %"acc" = alloca i64
  store i64 0, i64* %"acc"
  %"i" = alloca i64
  store i64 1, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", 100000001
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"acc_load" = load i64, i64* %"acc"
  %"i_load" = load i64, i64* %"i"
  %"add" = add i64 %"acc_load", %"i_load"
  store i64 %"add", i64* %"acc"
  %"t_load" = load i64, i64* %"t"
  %"icmp" = icmp slt i64 %"t_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %".16" = bitcast [1 x i8]* @"str_0" to i8*
  %".17" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".17", i8* %".16")
  %"acc_load.1" = load i64, i64* %"acc"
  %".18" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %".19" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".19", i64 %"acc_load.1")
  %".20" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".20")
  ret i64 0
if_then:
  store i64 0, i64* %"acc"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  br label %"for_inc"
}

@"str_0" = constant [1 x i8] c"\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"