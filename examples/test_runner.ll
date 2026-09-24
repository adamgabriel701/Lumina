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
define i64 @"somar"(i64 %".1", i64 %".2")
{
somar_entry:
  %"a" = alloca i64
  store i64 %".1", i64* %"a"
  %"b" = alloca i64
  store i64 %".2", i64* %"b"
  br label %"somar_body"
somar_body:
  %"a_load" = load i64, i64* %"a"
  %"b_load" = load i64, i64* %"b"
  %"add" = add i64 %"a_load", %"b_load"
  ret i64 %"add"
}

define i64 @"test_deve_somar_dois_numeros_positivos"()
{
test_deve_somar_dois_numeros_positivos_entry:
  br label %"test_deve_somar_dois_numeros_positivos_body"
test_deve_somar_dois_numeros_positivos_body:
  %"somar_call" = call i64 @"somar"(i64 2, i64 3)
  %"res" = alloca i64
  store i64 %"somar_call", i64* %"res"
  %"res_load" = load i64, i64* %"res"
  %"icmp" = icmp eq i64 %"res_load", 5
  br i1 %"icmp", label %"assert_ok", label %"assert_fail"
assert_ok:
  ret i64 0
assert_fail:
  %".5" = call i32 @"fflush"(i8* null)
  call void @"abort"()
  unreachable
}

define i64 @"test_deve_somar_numeros_negativos"()
{
test_deve_somar_numeros_negativos_entry:
  br label %"test_deve_somar_numeros_negativos_body"
test_deve_somar_numeros_negativos_body:
  %"neg" = sub i64 0, 5
  %"somar_call" = call i64 @"somar"(i64 %"neg", i64 10)
  %"res" = alloca i64
  store i64 %"somar_call", i64* %"res"
  %"res_load" = load i64, i64* %"res"
  %"icmp" = icmp eq i64 %"res_load", 5
  br i1 %"icmp", label %"assert_ok", label %"assert_fail"
assert_ok:
  ret i64 0
assert_fail:
  %".5" = call i32 @"fflush"(i8* null)
  call void @"abort"()
  unreachable
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [25 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"test_deve_somar_dois_numeros_positivos_call" = call i64 @"test_deve_somar_dois_numeros_positivos"()
  %".10" = bitcast [16 x i8]* @"str_3" to i8*
  %".11" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".10")
  %".12" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %"test_deve_somar_numeros_negativos_call" = call i64 @"test_deve_somar_numeros_negativos"()
  %".13" = bitcast [16 x i8]* @"str_6" to i8*
  %".14" = bitcast [3 x i8]* @"str_7" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %".15" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [38 x i8]* @"str_9" to i8*
  %".17" = bitcast [3 x i8]* @"str_10" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".17", i8* %".16")
  %".18" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
declare i32 @"fflush"(i8* %".1")

declare void @"abort"()

@"str_0" = constant [25 x i8] c"Iniciando Test Runner...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [16 x i8] c"Teste 1 passou.\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c"\0a\00"
@"str_6" = constant [16 x i8] c"Teste 2 passou.\00"
@"str_7" = constant [3 x i8] c"%s\00"
@"str_8" = constant [2 x i8] c"\0a\00"
@"str_9" = constant [38 x i8] c"Todos os testes passaram com sucesso!\00"
@"str_10" = constant [3 x i8] c"%s\00"
@"str_11" = constant [2 x i8] c"\0a\00"