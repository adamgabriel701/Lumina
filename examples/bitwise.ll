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
  %"bitand" = and i64 12, 10
  %".7" = bitcast [4 x i8]* @"str_0" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".7", i64 %"bitand")
  %".8" = bitcast [2 x i8]* @"str_1" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".8")
  %"bitor" = or i64 12, 10
  %".9" = bitcast [4 x i8]* @"str_2" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".9", i64 %"bitor")
  %".10" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %"bitxor" = xor i64 12, 10
  %".11" = bitcast [4 x i8]* @"str_4" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".11", i64 %"bitxor")
  %".12" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %"shl" = shl i64 1, 4
  %".13" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".13", i64 %"shl")
  %".14" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %"ashr" = ashr i64 256, 2
  %".15" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"ashr")
  %".16" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [4 x i8] c"%ld\00"
@"str_1" = constant [2 x i8] c"\0a\00"
@"str_2" = constant [4 x i8] c"%ld\00"
@"str_3" = constant [2 x i8] c"\0a\00"
@"str_4" = constant [4 x i8] c"%ld\00"
@"str_5" = constant [2 x i8] c"\0a\00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"