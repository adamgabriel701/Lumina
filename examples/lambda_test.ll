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
define i64 @"aplicar_fn"(i64 %".1", i8* %".2")
{
aplicar_fn_entry:
  %"val" = alloca i64
  store i64 %".1", i64* %"val"
  %"callback" = alloca i8*
  store i8* %".2", i8** %"callback"
  br label %"aplicar_fn_body"
aplicar_fn_body:
  %".7" = bitcast [19 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"val_load" = load i64, i64* %"val"
  %"mul" = mul i64 %"val_load", 2
  ret i64 %"mul"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [20 x i8]* @"str_3" to i8*
  %".8" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"closure_env_0" = call i8* @"GC_malloc"(i64 16)
  %"closure_env_typed_0" = bitcast i8* %"closure_env_0" to {}*
  %"closure___closure_0" = call i8* @"GC_malloc"(i64 16)
  %"closure_i8pp" = bitcast i8* %"closure___closure_0" to i8**
  %"fn_as_ptr" = bitcast i64 (i8*, i64)* @"__closure_0" to i8*
  store i8* %"fn_as_ptr", i8** %"closure_i8pp"
  %"env_slot" = getelementptr i8*, i8** %"closure_i8pp", i64 1
  store i8* %"closure_env_0", i8** %"env_slot"
  %"minha_fn" = alloca i8*
  store i8* %"closure___closure_0", i8** %"minha_fn"
  %"minha_fn_load" = load i8*, i8** %"minha_fn"
  %"aplicar_fn_call" = call i64 @"aplicar_fn"(i64 5, i8* %"minha_fn_load")
  %"res" = alloca i64
  store i64 %"aplicar_fn_call", i64* %"res"
  %".14" = bitcast [11 x i8]* @"str_6" to i8*
  %".15" = bitcast [3 x i8]* @"str_7" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".15", i8* %".14")
  %"res_load" = load i64, i64* %"res"
  %".16" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [4 x i8]* @"str_9" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".17", i64 %"res_load")
  %".18" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [19 x i8] c"Callback recebido!\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [20 x i8] c"Testando Lambdas...\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c"\0a\00"
define i64 @"__closure_0"(i8* %".1", i64 %".2")
{
entry:
  %"env_typed_inner" = bitcast i8* %".1" to {}*
  %"x" = alloca i64
  store i64 %".2", i64* %"x"
  %"x_load" = load i64, i64* %"x"
  %"add" = add i64 %"x_load", 10
  ret i64 %"add"
}

@"str_6" = constant [11 x i8] c"Resultado:\00"
@"str_7" = constant [3 x i8] c"%s\00"
@"str_8" = constant [2 x i8] c" \00"
@"str_9" = constant [4 x i8] c"%ld\00"
@"str_10" = constant [2 x i8] c"\0a\00"