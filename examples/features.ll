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
define void @"processar_dados"(i64 %".1")
{
processar_dados_entry:
  %"id" = alloca i64
  store i64 %".1", i64* %"id"
  br label %"processar_dados_body"
processar_dados_body:
  %".5" = bitcast [33 x i8]* @"str_0" to i8*
  %".6" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".6", i8* %".5")
  %"id_load" = load i64, i64* %"id"
  %".7" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".7")
  %".8" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".8", i64 %"id_load")
  %".9" = bitcast [4 x i8]* @"str_4" to i8*
  %".10" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %".11" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".9")
  %".12" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %"id_load.1" = load i64, i64* %"id"
  %"icmp" = icmp eq i64 %"id_load.1", 2
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %".14" = bitcast [34 x i8]* @"str_8" to i8*
  %".15" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".15", i8* %".14")
  %".16" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [26 x i8]* @"str_11" to i8*
  %".18" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"id_load.2" = load i64, i64* %"id"
  %".19" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [4 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".20", i64 %"id_load.2")
  %".21" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".21")
  ret void
if_else:
  br label %"if_end"
if_end:
  %".24" = bitcast [33 x i8]* @"str_16" to i8*
  %".25" = bitcast [3 x i8]* @"str_17" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %".24")
  %".26" = bitcast [2 x i8]* @"str_18" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".26")
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
  call void @"processar_dados"(i64 1)
  call void @"processar_dados"(i64 2)
  %"porta" = alloca i64
  store i64 8080, i64* %"porta"
  %".8" = bitcast [26 x i8]* @"str_19" to i8*
  %".9" = bitcast [3 x i8]* @"str_20" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".9", i8* %".8")
  %"porta_load" = load i64, i64* %"porta"
  %".10" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %".11" = bitcast [4 x i8]* @"str_22" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".11", i64 %"porta_load")
  %".12" = bitcast [4 x i8]* @"str_23" to i8*
  %".13" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".13")
  %".14" = bitcast [3 x i8]* @"str_25" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".12")
  %".15" = bitcast [2 x i8]* @"str_26" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [33 x i8] c"Processando dados para o usuario\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [4 x i8] c"...\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [34 x i8] c"Erro encontrado, retornando cedo!\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c"\0a\00"
@"str_11" = constant [26 x i8] c"Liberando recursos do ID:\00"
@"str_12" = constant [3 x i8] c"%s\00"
@"str_13" = constant [2 x i8] c" \00"
@"str_14" = constant [4 x i8] c"%ld\00"
@"str_15" = constant [2 x i8] c"\0a\00"
@"str_16" = constant [33 x i8] c"Processo conclu\c3\addo com sucesso.\00"
@"str_17" = constant [3 x i8] c"%s\00"
@"str_18" = constant [2 x i8] c"\0a\00"
@"str_19" = constant [26 x i8] c"Servidor rodando na porta\00"
@"str_20" = constant [3 x i8] c"%s\00"
@"str_21" = constant [2 x i8] c" \00"
@"str_22" = constant [4 x i8] c"%ld\00"
@"str_23" = constant [4 x i8] c"...\00"
@"str_24" = constant [2 x i8] c" \00"
@"str_25" = constant [3 x i8] c"%s\00"
@"str_26" = constant [2 x i8] c"\0a\00"