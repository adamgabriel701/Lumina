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
declare i64 @"pthread_create"(i8* %".1", i64 %".2", i64 %".3", i8* %".4")

declare i64 @"pthread_join"(i64 %".1", i64 %".2")

declare i64 @"usleep"(i64 %".1")

define i8* @"worker"(i8* %".1")
{
worker_entry:
  %"arg" = alloca i8*
  store i8* %".1", i8** %"arg"
  br label %"worker_body"
worker_body:
  %"arg_load" = load i8*, i8** %"arg"
  %".5" = getelementptr i8, i8* %"arg_load", i64 0
  %"ptr_idx_load" = load i8, i8* %".5"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"sub" = sub i64 %"idx_sext", 48
  %"id" = alloca i64
  store i64 %"sub", i64* %"id"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 3
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %".10" = bitcast [7 x i8]* @"str_0" to i8*
  %".11" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".10")
  %"id_load" = load i64, i64* %"id"
  %".12" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %".13" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".13", i64 %"id_load")
  %".14" = bitcast [10 x i8]* @"str_4" to i8*
  %".15" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".16", i8* %".14")
  %"i_load.1" = load i64, i64* %"i"
  %".17" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i64 %"i_load.1")
  %".19" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %"usleep_call" = call i64 @"usleep"(i64 100000)
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  %".22" = bitcast [1 x i8]* @"str_10" to i8*
  ret i8* %".22"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"t1_stack" = alloca [1 x i64]
  %"t1_first" = getelementptr [1 x i64], [1 x i64]* %"t1_stack", i32 0, i32 0
  %"t1" = alloca i64*
  store i64* %"t1_first", i64** %"t1"
  %"t2_stack" = alloca [1 x i64]
  %"t2_first" = getelementptr [1 x i64], [1 x i64]* %"t2_stack", i32 0, i32 0
  %"t2" = alloca i64*
  store i64* %"t2_first", i64** %"t2"
  %".9" = bitcast [21 x i8]* @"str_11" to i8*
  %".10" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".10", i8* %".9")
  %".11" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".11")
  %"t1_load" = load i64*, i64** %"t1"
  %"arg_ptr_cast" = bitcast i64* %"t1_load" to i8*
  %"worker_rawfn" = bitcast i8* (i8*)* @"worker" to i8*
  %"arg_ptr_to_int" = ptrtoint i8* %"worker_rawfn" to i64
  %".12" = bitcast [2 x i8]* @"str_14" to i8*
  %"pthread_create_call" = call i64 @"pthread_create"(i8* %"arg_ptr_cast", i64 0, i64 %"arg_ptr_to_int", i8* %".12")
  %"r1" = alloca i64
  store i64 %"pthread_create_call", i64* %"r1"
  %"t2_load" = load i64*, i64** %"t2"
  %"arg_ptr_cast.1" = bitcast i64* %"t2_load" to i8*
  %"worker_rawfn.1" = bitcast i8* (i8*)* @"worker" to i8*
  %"arg_ptr_to_int.1" = ptrtoint i8* %"worker_rawfn.1" to i64
  %".14" = bitcast [2 x i8]* @"str_15" to i8*
  %"pthread_create_call.1" = call i64 @"pthread_create"(i8* %"arg_ptr_cast.1", i64 0, i64 %"arg_ptr_to_int.1", i8* %".14")
  %"r2" = alloca i64
  store i64 %"pthread_create_call.1", i64* %"r2"
  %"r1_load" = load i64, i64* %"r1"
  %"icmp" = icmp ne i64 %"r1_load", 0
  br i1 %"icmp", label %"or_end", label %"or_rhs"
or_rhs:
  %"r2_load" = load i64, i64* %"r2"
  %"icmp.1" = icmp ne i64 %"r2_load", 0
  br label %"or_end"
or_end:
  %"or_result" = phi  i1 [1, %"main_body"], [%"icmp.1", %"or_rhs"]
  br i1 %"or_result", label %"if_then", label %"if_else"
if_then:
  %".19" = bitcast [26 x i8]* @"str_16" to i8*
  %".20" = bitcast [3 x i8]* @"str_17" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %".21" = bitcast [2 x i8]* @"str_18" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %"ret_trunc" = trunc i64 1 to i32
  ret i32 %"ret_trunc"
if_else:
  br label %"if_end"
if_end:
  %"t1_load.1" = load i64*, i64** %"t1"
  %".24" = getelementptr i64, i64* %"t1_load.1", i64 0
  %"ptr_idx_load" = load i64, i64* %".24"
  %"pthread_join_call" = call i64 @"pthread_join"(i64 %"ptr_idx_load", i64 0)
  %"t2_load.1" = load i64*, i64** %"t2"
  %".25" = getelementptr i64, i64* %"t2_load.1", i64 0
  %"ptr_idx_load.1" = load i64, i64* %".25"
  %"pthread_join_call.1" = call i64 @"pthread_join"(i64 %"ptr_idx_load.1", i64 0)
  %".26" = bitcast [33 x i8]* @"str_19" to i8*
  %".27" = bitcast [3 x i8]* @"str_20" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".27", i8* %".26")
  %".28" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".28")
  %"ret_trunc.1" = trunc i64 0 to i32
  ret i32 %"ret_trunc.1"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [7 x i8] c"Thread\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [10 x i8] c"contagem:\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [1 x i8] c"\00"
@"str_11" = constant [21 x i8] c"Iniciando Threads...\00"
@"str_12" = constant [3 x i8] c"%s\00"
@"str_13" = constant [2 x i8] c"\0a\00"
@"str_14" = constant [2 x i8] c"1\00"
@"str_15" = constant [2 x i8] c"2\00"
@"str_16" = constant [26 x i8] c"Erro ao criar as threads!\00"
@"str_17" = constant [3 x i8] c"%s\00"
@"str_18" = constant [2 x i8] c"\0a\00"
@"str_19" = constant [33 x i8] c"Threads finalizadas com sucesso!\00"
@"str_20" = constant [3 x i8] c"%s\00"
@"str_21" = constant [2 x i8] c"\0a\00"