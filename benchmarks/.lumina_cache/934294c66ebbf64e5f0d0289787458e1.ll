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
define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"acc" = alloca i64
  store i64 0, i64* %"acc"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 1000000
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"acc_load" = load i64, i64* %"acc"
  %"i_load.1" = load i64, i64* %"i"
  %"add" = add i64 %"acc_load", %"i_load.1"
  %"black_box_call" = call i64 asm sideeffect "", "=r,0"(i64 %"add")
  store i64 %"black_box_call", i64* %"acc"
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.2", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  %"acc_load.1" = load i64, i64* %"acc"
  %".14" = bitcast [4 x i8]* @"str_0" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".14", i64 %"acc_load.1")
  %".15" = bitcast [2 x i8]* @"str_1" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [4 x i8] c"%ld\00"
@"str_1" = constant [2 x i8] c"\0a\00"