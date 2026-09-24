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
  %".7" = bitcast [33 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %".10" = bitcast [16 x i8]* @"str_3" to i8*
  %".11" = bitcast [30 x i8]* @"str_4" to i8*
  %".12" = bitcast [2 x i8]* @"str_5" to i8*
  %"wf_fopen" = call i8* @"fopen"(i8* %".10", i8* %".12")
  %"wf_fputs" = call i32 @"fputs"(i8* %".11", i8* %"wf_fopen")
  %"wf_fclose" = call i32 @"fclose"(i8* %"wf_fopen")
  %".13" = bitcast [16 x i8]* @"str_6" to i8*
  %"read_file_async_call" = call i8* @"read_file_async"(i8* %".13")
  %"dados" = alloca i8*
  store i8* %"read_file_async_call", i8** %"dados"
  %".15" = bitcast [16 x i8]* @"str_7" to i8*
  %".16" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".16", i8* %".15")
  %"dados_load" = load i8*, i8** %"dados"
  %".17" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [3 x i8]* @"str_10" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %"dados_load")
  %".19" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
declare i64 @"open"(i8* %".1", i64 %".2")

declare i64 @"read"(i64 %".1", i64* %".2", i64 %".3")

declare i64 @"close"(i64 %".1")

define i8* @"read_file_async"(i8* %".1")
{
read_file_async_entry:
  %"path" = alloca i8*
  store i8* %".1", i8** %"path"
  br label %"read_file_async_body"
read_file_async_body:
  %"path_load" = load i8*, i8** %"path"
  %"bitor" = or i64 0, 2048
  %"open_call" = call i64 @"open"(i8* %"path_load", i64 %"bitor")
  %"fd" = alloca i64
  store i64 %"open_call", i64* %"fd"
  %"fd_load" = load i64, i64* %"fd"
  %"icmp" = icmp slt i64 %"fd_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".7" = bitcast [5 x i8]* @"str_12" to i8*
  ret i8* %".7"
if_else:
  br label %"if_end"
if_end:
  %"buf_stack" = alloca [4096 x i8]
  %"buf_first" = getelementptr [4096 x i8], [4096 x i8]* %"buf_stack", i32 0, i32 0
  %"buf" = alloca i8*
  store i8* %"buf_first", i8** %"buf"
  %"fd_load.1" = load i64, i64* %"fd"
  %"buf_load" = load i8*, i8** %"buf"
  %"arg_ptr_cast" = bitcast i8* %"buf_load" to i64*
  %"read_call" = call i64 @"read"(i64 %"fd_load.1", i64* %"arg_ptr_cast", i64 4096)
  %"bytes_read" = alloca i64
  store i64 %"read_call", i64* %"bytes_read"
  %"bytes_read_load" = load i64, i64* %"bytes_read"
  %"icmp.1" = icmp sgt i64 %"bytes_read_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"buf_load.1" = load i8*, i8** %"buf"
  %"bytes_read_load.1" = load i64, i64* %"bytes_read"
  %"idx_ptr" = getelementptr i8, i8* %"buf_load.1", i64 %"bytes_read_load.1"
  %"elem_trunc" = trunc i64 0 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"fd_load.2" = load i64, i64* %"fd"
  %"close_call" = call i64 @"close"(i64 %"fd_load.2")
  %"buf_load.2" = load i8*, i8** %"buf"
  ret i8* %"buf_load.2"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"fd_load.3" = load i64, i64* %"fd"
  %"close_call.1" = call i64 @"close"(i64 %"fd_load.3")
  %".16" = bitcast [1 x i8]* @"str_13" to i8*
  ret i8* %".16"
}

declare i64 @"remove"(i8* %".1")

define i64 @"deletar_arquivo"(i8* %".1")
{
deletar_arquivo_entry:
  %"path" = alloca i8*
  store i8* %".1", i8** %"path"
  br label %"deletar_arquivo_body"
deletar_arquivo_body:
  %"path_load" = load i8*, i8** %"path"
  %"remove_call" = call i64 @"remove"(i8* %"path_load")
  ret i64 %"remove_call"
}

@"str_0" = constant [33 x i8] c"\f0\9f\9a\80 Testando I/O Ass\c3\adncrono...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [16 x i8] c"teste_async.txt\00"
@"str_4" = constant [30 x i8] c"Dados do arquivo ass\c3\adncrono!\00"
declare i8* @"fopen"(i8* %".1", i8* %".2")

declare i32 @"fputs"(i8* %".1", i8* %".2")

declare i32 @"fclose"(i8* %".1")

@"str_5" = constant [2 x i8] c"w\00"
@"str_6" = constant [16 x i8] c"teste_async.txt\00"
@"str_7" = constant [16 x i8] c"Conte\c3\bado lido:\00"
@"str_8" = constant [3 x i8] c"%s\00"
@"str_9" = constant [2 x i8] c" \00"
@"str_10" = constant [3 x i8] c"%s\00"
@"str_11" = constant [2 x i8] c"\0a\00"
@"str_12" = constant [5 x i8] c"ERRO\00"
@"str_13" = constant [1 x i8] c"\00"