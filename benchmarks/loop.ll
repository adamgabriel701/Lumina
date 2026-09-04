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

define i64 @"main"(i32 %".1", i8** %".2")
{
entry:
  %"sum" = alloca i64
  store i64 0, i64* %"sum"
  %"max" = alloca i64
  store i64 100000000, i64* %"max"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  %"max_val" = load i64, i64* %"max"
  br label %"for.cond"
for.cond:
  %"i_val" = load i64, i64* %"i"
  %"for_cond" = icmp slt i64 %"i_val", %"max_val"
  br i1 %"for_cond", label %"for.body", label %"for.end"
for.body:
  %"sum_val" = load i64, i64* %"sum"
  %"i_val.1" = load i64, i64* %"i"
  %"add_tmp" = add i64 %"sum_val", %"i_val.1"
  store i64 %"add_tmp", i64* %"sum"
  %"for_next" = add i64 %"i_val", 1
  store i64 %"for_next", i64* %"i"
  br label %"for.cond"
for.end:
  %".12" = bitcast [6 x i8]* @"str_0" to i8*
  %".13" = bitcast [4 x i8]* @"str_1" to i8*
  %".14" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %".12")
  %"sum_val.1" = load i64, i64* %"sum"
  %".15" = bitcast [4 x i8]* @"str_2" to i8*
  %".16" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"sum_val.1")
  %".17" = bitcast [2 x i8]* @"str_3" to i8*
  %".18" = call i32 (i8*, ...) @"printf"(i8* %".17")
  ret i64 0
}

@"str_0" = constant [6 x i8] c"Sum =\00"
@"str_1" = constant [4 x i8] c"%s \00"
@"str_2" = constant [4 x i8] c"%d \00"
@"str_3" = constant [2 x i8] c"\0a\00"