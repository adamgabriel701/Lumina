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
define i64 @"extrair_opcode"(i64 %".1")
{
extrair_opcode_entry:
  %"instrucao" = alloca i64
  store i64 %".1", i64* %"instrucao"
  br label %"extrair_opcode_body"
extrair_opcode_body:
  %"instrucao_load" = load i64, i64* %"instrucao"
  %"ashr" = ashr i64 %"instrucao_load", 8
  %"bitand" = and i64 %"ashr", 255
  ret i64 %"bitand"
}

define i64 @"extrair_endereco"(i64 %".1")
{
extrair_endereco_entry:
  %"instrucao" = alloca i64
  store i64 %".1", i64* %"instrucao"
  br label %"extrair_endereco_body"
extrair_endereco_body:
  %"instrucao_load" = load i64, i64* %"instrucao"
  %"bitand" = and i64 %"instrucao_load", 255
  ret i64 %"bitand"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"instrucao" = alloca i64
  store i64 41712, i64* %"instrucao"
  %"instrucao_load" = load i64, i64* %"instrucao"
  %"extrair_opcode_call" = call i64 @"extrair_opcode"(i64 %"instrucao_load")
  %"opcode" = alloca i64
  store i64 %"extrair_opcode_call", i64* %"opcode"
  %"instrucao_load.1" = load i64, i64* %"instrucao"
  %"extrair_endereco_call" = call i64 @"extrair_endereco"(i64 %"instrucao_load.1")
  %"endereco" = alloca i64
  store i64 %"extrair_endereco_call", i64* %"endereco"
  %".10" = bitcast [22 x i8]* @"str_0" to i8*
  %".11" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".10")
  %"instrucao_load.2" = load i64, i64* %"instrucao"
  %".12" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %".13" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".13", i64 %"instrucao_load.2")
  %".14" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [23 x i8]* @"str_5" to i8*
  %".16" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".16", i8* %".15")
  %"opcode_load" = load i64, i64* %"opcode"
  %".17" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i64 %"opcode_load")
  %".19" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [26 x i8]* @"str_10" to i8*
  %".21" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".20")
  %"endereco_load" = load i64, i64* %"endereco"
  %".22" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %".23" = bitcast [4 x i8]* @"str_13" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".23", i64 %"endereco_load")
  %".24" = bitcast [2 x i8]* @"str_14" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %"opcode_load.1" = load i64, i64* %"opcode"
  %"bitor" = or i64 %"opcode_load.1", 16
  %"combinado" = alloca i64
  store i64 %"bitor", i64* %"combinado"
  %".26" = bitcast [32 x i8]* @"str_15" to i8*
  %".27" = bitcast [3 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".27", i8* %".26")
  %"combinado_load" = load i64, i64* %"combinado"
  %".28" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".28")
  %".29" = bitcast [4 x i8]* @"str_18" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".29", i64 %"combinado_load")
  %".30" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [22 x i8] c"Instru\c3\a7\c3\a3o completa:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [23 x i8] c"Opcode extra\c3\addo (A2):\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [26 x i8] c"Endere\c3\a7o extra\c3\addo (F0):\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c" \00"
@"str_13" = constant [4 x i8] c"%ld\00"
@"str_14" = constant [2 x i8] c"\0a\00"
@"str_15" = constant [32 x i8] c"Opcode combinado com 0x10 (B2):\00"
@"str_16" = constant [3 x i8] c"%s\00"
@"str_17" = constant [2 x i8] c" \00"
@"str_18" = constant [4 x i8] c"%ld\00"
@"str_19" = constant [2 x i8] c"\0a\00"