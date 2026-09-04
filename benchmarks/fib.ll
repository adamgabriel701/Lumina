; ModuleID = "lumina_module"
target triple = "x86_64-pc-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

declare i32 @"sprintf"(i8* %".1", i8* %".2", ...)

declare i64 @"atoi"(i8* %".1")

declare i8* @"malloc"(i64 %".1")

declare void @"free"(i8* %".1")

declare i8* @"fopen"(i8* %".1", i8* %".2")

declare i8* @"fgets"(i8* %".1", i32 %".2", i8* %".3")

declare i32 @"fputs"(i8* %".1", i8* %".2")

declare void @"fclose"(i8* %".1")

define i64 @"fib"(i64 %".1")
{
entry:
  %"n" = alloca i64
  store i64 %".1", i64* %"n"
  %"n_val" = load i64, i64* %"n"
  %"cmp_tmp" = icmp sle i64 %"n_val", 1
  br i1 %"cmp_tmp", label %"if.then", label %"if.end"
if.then:
  %"n_val.1" = load i64, i64* %"n"
  ret i64 %"n_val.1"
if.end:
  %"n_val.2" = load i64, i64* %"n"
  %"sub_tmp" = sub i64 %"n_val.2", 1
  %"fib_call" = call i64 @"fib"(i64 %"sub_tmp")
  %"n_val.3" = load i64, i64* %"n"
  %"sub_tmp.1" = sub i64 %"n_val.3", 2
  %"fib_call.1" = call i64 @"fib"(i64 %"sub_tmp.1")
  %"add_tmp" = add i64 %"fib_call", %"fib_call.1"
  ret i64 %"add_tmp"
}

define i64 @"main"(i32 %".1", i8** %".2")
{
entry:
  %"fib_call" = call i64 @"fib"(i64 35)
  %"result" = alloca i64
  store i64 %"fib_call", i64* %"result"
  %".5" = bitcast [10 x i8]* @"str_0" to i8*
  %".6" = bitcast [4 x i8]* @"str_1" to i8*
  %".7" = call i32 (i8*, ...) @"printf"(i8* %".6", i8* %".5")
  %"result_val" = load i64, i64* %"result"
  %".8" = bitcast [4 x i8]* @"str_2" to i8*
  %".9" = call i32 (i8*, ...) @"printf"(i8* %".8", i64 %"result_val")
  %".10" = bitcast [2 x i8]* @"str_3" to i8*
  %".11" = call i32 (i8*, ...) @"printf"(i8* %".10")
  ret i64 0
}

@"str_0" = constant [10 x i8] c"Fib(35) =\00"
@"str_1" = constant [4 x i8] c"%s \00"
@"str_2" = constant [4 x i8] c"%d \00"
@"str_3" = constant [2 x i8] c"\0a\00"