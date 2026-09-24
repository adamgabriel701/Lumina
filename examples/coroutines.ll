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
@"g_resumed" = internal global i64 0
@"g_current_task" = internal global i64 0
define void @"task_a"()
{
task_a_entry:
  br label %"task_a_body"
task_a_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 3
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %".6" = bitcast [8 x i8]* @"str_0" to i8*
  %".7" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".7", i8* %".6")
  %"i_load.1" = load i64, i64* %"i"
  %".8" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".8")
  %".9" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".9", i64 %"i_load.1")
  %".10" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 1024)
  %"alloc_bytes_call.1" = call i8* @"GC_malloc"(i64 1024)
  %"swapcontext_call" = call i64 @"swapcontext"(i8* %"alloc_bytes_call", i8* %"alloc_bytes_call.1")
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
  %".7" = bitcast [27 x i8]* @"str_5" to i8*
  %".8" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 1024)
  %"getcontext_call" = call i64 @"getcontext"(i8* %"alloc_bytes_call")
  %"g_resumed_load" = load i64, i64* @"g_resumed"
  %"icmp" = icmp eq i64 %"g_resumed_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  store i64 1, i64* @"g_resumed"
  %".12" = bitcast [20 x i8]* @"str_8" to i8*
  %".13" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %".12")
  %".14" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".14")
  call void @"task_a"()
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %".17" = bitcast [55 x i8]* @"str_11" to i8*
  %".18" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %".19" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [20 x i8]* @"str_14" to i8*
  %".21" = bitcast [3 x i8]* @"str_15" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".20")
  %".22" = bitcast [2 x i8]* @"str_16" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
declare i64 @"getcontext"(i8* %".1")

declare void @"makecontext"(i8* %".1", i64 %".2", i64 %".3", i64 %".4")

declare i64 @"swapcontext"(i8* %".1", i8* %".2")

define void @"run"()
{
run_entry:
  br label %"run_body"
run_body:
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 1024)
  %"alloc_bytes_call.1" = call i8* @"GC_malloc"(i64 1024)
  %"swapcontext_call" = call i64 @"swapcontext"(i8* %"alloc_bytes_call", i8* %"alloc_bytes_call.1")
  ret void
}

define void @"task_wrapper"(i64 %".1")
{
task_wrapper_entry:
  %"func" = alloca i64
  store i64 %".1", i64* %"func"
  br label %"task_wrapper_body"
task_wrapper_body:
  %".5" = bitcast [24 x i8]* @"str_17" to i8*
  %".6" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".6", i8* %".5")
  %".7" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".7")
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 1024)
  %"alloc_bytes_call.1" = call i8* @"GC_malloc"(i64 1024)
  %"swapcontext_call" = call i64 @"swapcontext"(i8* %"alloc_bytes_call", i8* %"alloc_bytes_call.1")
  ret void
}

@"str_0" = constant [8 x i8] c"Task A:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [27 x i8] c"Iniciando Green Threads...\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [20 x i8] c"Iniciando Task A...\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c"\0a\00"
@"str_11" = constant [55 x i8] c"Task A conclu\c3\adda ou cedeu CPU. Continuando na main...\00"
@"str_12" = constant [3 x i8] c"%s\00"
@"str_13" = constant [2 x i8] c"\0a\00"
@"str_14" = constant [20 x i8] c"Fim do escalonador.\00"
@"str_15" = constant [3 x i8] c"%s\00"
@"str_16" = constant [2 x i8] c"\0a\00"
@"str_17" = constant [24 x i8] c"Corrotina executando...\00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c"\0a\00"