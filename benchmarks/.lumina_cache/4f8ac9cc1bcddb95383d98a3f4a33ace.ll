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
define i64 @"fib"(i64 %".1")
{
fib_entry:
  %"n" = alloca i64
  store i64 %".1", i64* %"n"
  br label %"fib_body"
fib_body:
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp sle i64 %"n_load", 1
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"n_load.1" = load i64, i64* %"n"
  ret i64 %"n_load.1"
if_else:
  br label %"if_end"
if_end:
  %"n_load.2" = load i64, i64* %"n"
  %"sub" = sub i64 %"n_load.2", 1
  %"fib_call" = call i64 @"fib"(i64 %"sub")
  %"n_load.3" = load i64, i64* %"n"
  %"sub.1" = sub i64 %"n_load.3", 2
  %"fib_call.1" = call i64 @"fib"(i64 %"sub.1")
  %"add" = add i64 %"fib_call", %"fib_call.1"
  ret i64 %"add"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"n" = alloca i64
  store i64 35, i64* %"n"
  %"argv_load" = load i8**, i8*** @"__lumina_argv"
  %"argv_elem_ptr" = getelementptr i8*, i8** %"argv_load", i64 1
  %"argv_elem" = load i8*, i8** %"argv_elem_ptr"
  %"len_str" = call i64 @"strlen"(i8* %"argv_elem")
  %"icmp" = icmp sgt i64 %"len_str", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"argv_load.1" = load i8**, i8*** @"__lumina_argv"
  %"argv_elem_ptr.1" = getelementptr i8*, i8** %"argv_load.1", i64 1
  %"argv_elem.1" = load i8*, i8** %"argv_elem_ptr.1"
  %"atoi_call" = call i64 @"atoi"(i8* %"argv_elem.1")
  store i64 %"atoi_call", i64* %"n"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %".12" = bitcast [1 x i8]* @"str_0" to i8*
  %".13" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %".12")
  %"n_load" = load i64, i64* %"n"
  %"fib_call" = call i64 @"fib"(i64 %"n_load")
  %".14" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"fib_call")
  %".16" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [1 x i8] c"\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"