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
define i64 @"saudacao"(i8* %".1")
{
saudacao_entry:
  %"nome" = alloca i8*
  store i8* %".1", i8** %"nome"
  br label %"saudacao_body"
saudacao_body:
  %".5" = bitcast [5 x i8]* @"str_0" to i8*
  %"nome_load" = load i8*, i8** %"nome"
  %"sconcat_len1" = call i64 @"strlen"(i8* %".5")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"nome_load")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".5")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"nome_load")
  %"msg" = alloca i8*
  store i8* %"sconcat_buf", i8** %"msg"
  %"msg_load" = load i8*, i8** %"msg"
  %".7" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".7", i8* %"msg_load")
  %".8" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".8")
  ret i64 0
}

define void @"criar_log"()
{
criar_log_entry:
  br label %"criar_log_body"
criar_log_body:
  %".3" = bitcast [30 x i8]* @"str_3" to i8*
  %"conteudo" = alloca i8*
  store i8* %".3", i8** %"conteudo"
  %".5" = bitcast [8 x i8]* @"str_4" to i8*
  %"conteudo_load" = load i8*, i8** %"conteudo"
  %".6" = bitcast [2 x i8]* @"str_5" to i8*
  %"wf_fopen" = call i8* @"fopen"(i8* %".5", i8* %".6")
  %"wf_fputs" = call i32 @"fputs"(i8* %"conteudo_load", i8* %"wf_fopen")
  %"wf_fclose" = call i32 @"fclose"(i8* %"wf_fopen")
  ret void
}

@"str_0" = constant [5 x i8] c"Ola \00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [30 x i8] c"Sistema iniciado com sucesso!\00"
@"str_4" = constant [8 x i8] c"log.txt\00"
declare i8* @"fopen"(i8* %".1", i8* %".2")

declare i32 @"fputs"(i8* %".1", i8* %".2")

declare i32 @"fclose"(i8* %".1")

@"str_5" = constant [2 x i8] c"w\00"