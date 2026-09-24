; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"malloc"(i64 %".1")

declare void @"free"(i8* %".1")

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
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"limit" = alloca i64
  store i64 10000000, i64* %"limit"
  %"limit_load" = load i64, i64* %"limit"
  %"alloc_bytes_call" = call i8* @"malloc"(i64 %"limit_load")
  %"primes" = alloca i8*
  store i8* %"alloc_bytes_call", i8** %"primes"
  %"limit_load.1" = load i64, i64* %"limit"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", %"limit_load.1"
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"primes_load" = load i8*, i8** %"primes"
  %"i_load" = load i64, i64* %"i"
  %".12" = getelementptr i8, i8* %"primes_load", i64 %"i_load"
  %"idx_trunc" = trunc i64 1 to i8
  store i8 %"idx_trunc", i8* %".12"
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %"primes_load.1" = load i8*, i8** %"primes"
  %".17" = getelementptr i8, i8* %"primes_load.1", i64 0
  %"idx_trunc.1" = trunc i64 0 to i8
  store i8 %"idx_trunc.1", i8* %".17"
  %"primes_load.2" = load i8*, i8** %"primes"
  %".19" = getelementptr i8, i8* %"primes_load.2", i64 1
  %"idx_trunc.2" = trunc i64 0 to i8
  store i8 %"idx_trunc.2", i8* %".19"
  %"p" = alloca i64
  store i64 2, i64* %"p"
  br label %"while_cond"
while_cond:
  %"p_load" = load i64, i64* %"p"
  %"p_load.1" = load i64, i64* %"p"
  %"mul" = mul i64 %"p_load", %"p_load.1"
  %"limit_load.2" = load i64, i64* %"limit"
  %"icmp" = icmp slt i64 %"mul", %"limit_load.2"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"primes_load.3" = load i8*, i8** %"primes"
  %"p_load.2" = load i64, i64* %"p"
  %".24" = getelementptr i8, i8* %"primes_load.3", i64 %"p_load.2"
  %"ptr_idx_load" = load i8, i8* %".24"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"icmp.1" = icmp eq i64 %"idx_sext", 1
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"count" = alloca i64
  store i64 0, i64* %"count"
  %"limit_load.4" = load i64, i64* %"limit"
  %"i.2" = alloca i64
  store i64 0, i64* %"i.2"
  br label %"for_cond.2"
if_then:
  %"p_load.3" = load i64, i64* %"p"
  %"p_load.4" = load i64, i64* %"p"
  %"mul.1" = mul i64 %"p_load.3", %"p_load.4"
  %"i.1" = alloca i64
  store i64 %"mul.1", i64* %"i.1"
  br label %"while_cond.1"
if_else:
  br label %"if_end"
if_end:
  %"p_load.6" = load i64, i64* %"p"
  %"add.1" = add i64 %"p_load.6", 1
  store i64 %"add.1", i64* %"p"
  br label %"while_cond"
while_cond.1:
  %"i_load.1" = load i64, i64* %"i.1"
  %"limit_load.3" = load i64, i64* %"limit"
  %"icmp.2" = icmp slt i64 %"i_load.1", %"limit_load.3"
  br i1 %"icmp.2", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"primes_load.4" = load i8*, i8** %"primes"
  %"i_load.2" = load i64, i64* %"i.1"
  %".29" = getelementptr i8, i8* %"primes_load.4", i64 %"i_load.2"
  %"idx_trunc.3" = trunc i64 0 to i8
  store i8 %"idx_trunc.3", i8* %".29"
  %"i_load.3" = load i64, i64* %"i.1"
  %"p_load.5" = load i64, i64* %"p"
  %"add" = add i64 %"i_load.3", %"p_load.5"
  store i64 %"add", i64* %"i.1"
  br label %"while_cond.1"
while_end.1:
  br label %"if_end"
for_cond.2:
  %"for_curr.1" = load i64, i64* %"i.2"
  %"for_cond.3" = icmp slt i64 %"for_curr.1", %"limit_load.4"
  br i1 %"for_cond.3", label %"for_body.1", label %"for_end.1"
for_body.1:
  %"primes_load.5" = load i8*, i8** %"primes"
  %"i_load.4" = load i64, i64* %"i.2"
  %".41" = getelementptr i8, i8* %"primes_load.5", i64 %"i_load.4"
  %"ptr_idx_load.1" = load i8, i8* %".41"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"icmp.3" = icmp eq i64 %"idx_sext.1", 1
  br i1 %"icmp.3", label %"if_then.1", label %"if_else.1"
for_inc.1:
  %"for_curr_inc.1" = load i64, i64* %"i.2"
  %"for_next.1" = add i64 %"for_curr_inc.1", 1
  store i64 %"for_next.1", i64* %"i.2"
  br label %"for_cond.2"
for_end.1:
  %".49" = bitcast [1 x i8]* @"str_0" to i8*
  %".50" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".50", i8* %".49")
  %"count_load.1" = load i64, i64* %"count"
  %".51" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".51")
  %".52" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".52", i64 %"count_load.1")
  %".53" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".53")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
if_then.1:
  %"count_load" = load i64, i64* %"count"
  %"add.2" = add i64 %"count_load", 1
  store i64 %"add.2", i64* %"count"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  br label %"for_inc.1"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [1 x i8] c"\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"