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
define %"Result"* @"dividir"(i64 %".1", i64 %".2")
{
dividir_entry:
  %"a" = alloca i64
  store i64 %".1", i64* %"a"
  %"b" = alloca i64
  store i64 %".2", i64* %"b"
  br label %"dividir_body"
dividir_body:
  %"b_load" = load i64, i64* %"b"
  %"icmp" = icmp eq i64 %"b_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"Result_lit" = call i8* @"GC_malloc"(i64 16)
  %"Result_cast" = bitcast i8* %"Result_lit" to %"Result"*
  %"tag_ptr" = getelementptr %"Result", %"Result"* %"Result_cast", i32 0, i32 0
  store i32 1, i32* %"tag_ptr"
  %"payload_ptr_0" = getelementptr %"Result", %"Result"* %"Result_cast", i32 0, i32 1
  store i64 1, i64* %"payload_ptr_0"
  ret %"Result"* %"Result_cast"
if_else:
  br label %"if_end"
if_end:
  %"Result_lit.1" = call i8* @"GC_malloc"(i64 16)
  %"Result_cast.1" = bitcast i8* %"Result_lit.1" to %"Result"*
  %"tag_ptr.1" = getelementptr %"Result", %"Result"* %"Result_cast.1", i32 0, i32 0
  store i32 0, i32* %"tag_ptr.1"
  %"payload_ptr_0.1" = getelementptr %"Result", %"Result"* %"Result_cast.1", i32 0, i32 1
  %"a_load" = load i64, i64* %"a"
  %"b_load.1" = load i64, i64* %"b"
  %"div" = sdiv i64 %"a_load", %"b_load.1"
  store i64 %"div", i64* %"payload_ptr_0.1"
  ret %"Result"* %"Result_cast.1"
}

define %"Result"* @"processar"()
{
processar_entry:
  br label %"processar_body"
processar_body:
  %"dividir_call" = call %"Result"* @"dividir"(i64 10, i64 0)
  %"prop_tag_ptr" = getelementptr %"Result", %"Result"* %"dividir_call", i32 0, i32 0
  %"prop_tag" = load i32, i32* %"prop_tag_ptr"
  %"prop_iserr" = icmp ne i32 %"prop_tag", 0
  br i1 %"prop_iserr", label %"prop_err", label %"prop_ok"
prop_err:
  ret %"Result"* %"dividir_call"
prop_ok:
  %"prop_payload_ptr" = getelementptr %"Result", %"Result"* %"dividir_call", i32 0, i32 1
  %"prop_payload" = load i64, i64* %"prop_payload_ptr"
  %"val" = alloca i64
  store i64 %"prop_payload", i64* %"val"
  %".6" = bitcast [18 x i8]* @"str_0" to i8*
  %".7" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".7", i8* %".6")
  %"val_load" = load i64, i64* %"val"
  %".8" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".8")
  %".9" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".9", i64 %"val_load")
  %".10" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".10")
  %"Result_lit" = call i8* @"GC_malloc"(i64 16)
  %"Result_cast" = bitcast i8* %"Result_lit" to %"Result"*
  %"tag_ptr" = getelementptr %"Result", %"Result"* %"Result_cast", i32 0, i32 0
  store i32 0, i32* %"tag_ptr"
  %"payload_ptr_0" = getelementptr %"Result", %"Result"* %"Result_cast", i32 0, i32 1
  store i64 100, i64* %"payload_ptr_0"
  ret %"Result"* %"Result_cast"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"processar_call" = call %"Result"* @"processar"()
  %"res" = alloca %"Result"*
  store %"Result"* %"processar_call", %"Result"** %"res"
  %"res_load" = load %"Result"*, %"Result"** %"res"
  br label %"match_next_0"
match_end:
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
match_next_0:
  br label %"match_test_0"
match_test_0:
  %"match_tag_ptr_0" = getelementptr %"Result", %"Result"* %"res_load", i32 0, i32 0
  %"match_tag_0" = load i32, i32* %"match_tag_ptr_0"
  %"match_tag_eq_0" = icmp eq i32 %"match_tag_0", 0
  br i1 %"match_tag_eq_0", label %"match_bind_0", label %"match_next_1"
match_bind_0:
  %"payload_ptr_v" = getelementptr %"Result", %"Result"* %"res_load", i32 0, i32 1
  %"payload_v" = load i64, i64* %"payload_ptr_v"
  %"v" = alloca i64
  store i64 %"payload_v", i64* %"v"
  br label %"match_body_0"
match_body_0:
  %".13" = bitcast [33 x i8]* @"str_5" to i8*
  %".14" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %"v_load" = load i64, i64* %"v"
  %".15" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".16", i64 %"v_load")
  %".17" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".17")
  br label %"match_end"
match_next_1:
  br label %"match_test_1"
match_test_1:
  %"match_tag_ptr_1" = getelementptr %"Result", %"Result"* %"res_load", i32 0, i32 0
  %"match_tag_1" = load i32, i32* %"match_tag_ptr_1"
  %"match_tag_eq_1" = icmp eq i32 %"match_tag_1", 1
  br i1 %"match_tag_eq_1", label %"match_bind_1", label %"match_next_2"
match_bind_1:
  %"payload_ptr_e" = getelementptr %"Result", %"Result"* %"res_load", i32 0, i32 1
  %"payload_e" = load i64, i64* %"payload_ptr_e"
  %"e" = alloca i64
  store i64 %"payload_e", i64* %"e"
  br label %"match_body_1"
match_body_1:
  %".23" = bitcast [27 x i8]* @"str_10" to i8*
  %".24" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".24", i8* %".23")
  %"e_load" = load i64, i64* %"e"
  %".25" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".25")
  %".26" = bitcast [4 x i8]* @"str_13" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".26", i64 %"e_load")
  %".27" = bitcast [2 x i8]* @"str_14" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".27")
  br label %"match_end"
match_next_2:
  br label %"match_end"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [18 x i8] c"Deu certo! Valor:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [33 x i8] c"Processo conclu\c3\addo com sucesso:\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [27 x i8] c"Ocorreu um erro propagado:\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c" \00"
@"str_13" = constant [4 x i8] c"%ld\00"
@"str_14" = constant [2 x i8] c"\0a\00"