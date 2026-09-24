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

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [43 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"dividir_call" = call %"Result"* @"dividir"(i64 10, i64 2)
  %"res1" = alloca %"Result"*
  store %"Result"* %"dividir_call", %"Result"** %"res1"
  %"dividir_call.1" = call %"Result"* @"dividir"(i64 10, i64 0)
  %"res2" = alloca %"Result"*
  store %"Result"* %"dividir_call.1", %"Result"** %"res2"
  %"res1_load" = load %"Result"*, %"Result"** %"res1"
  br label %"match_next_0"
match_end:
  %"res2_load" = load %"Result"*, %"Result"** %"res2"
  br label %"match_next_0.1"
match_next_0:
  br label %"match_test_0"
match_test_0:
  %"match_tag_ptr_0" = getelementptr %"Result", %"Result"* %"res1_load", i32 0, i32 0
  %"match_tag_0" = load i32, i32* %"match_tag_ptr_0"
  %"match_tag_eq_0" = icmp eq i32 %"match_tag_0", 0
  br i1 %"match_tag_eq_0", label %"match_bind_0", label %"match_next_1"
match_bind_0:
  %"payload_ptr_val" = getelementptr %"Result", %"Result"* %"res1_load", i32 0, i32 1
  %"payload_val" = load i64, i64* %"payload_ptr_val"
  %"val" = alloca i64
  store i64 %"payload_val", i64* %"val"
  br label %"match_body_0"
match_body_0:
  %".17" = bitcast [25 x i8]* @"str_3" to i8*
  %".18" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"val_load" = load i64, i64* %"val"
  %".19" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".20", i64 %"val_load")
  %".21" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".21")
  br label %"match_end"
match_next_1:
  br label %"match_test_1"
match_test_1:
  %"match_tag_ptr_1" = getelementptr %"Result", %"Result"* %"res1_load", i32 0, i32 0
  %"match_tag_1" = load i32, i32* %"match_tag_ptr_1"
  %"match_tag_eq_1" = icmp eq i32 %"match_tag_1", 1
  br i1 %"match_tag_eq_1", label %"match_bind_1", label %"match_next_2"
match_bind_1:
  %"payload_ptr_e" = getelementptr %"Result", %"Result"* %"res1_load", i32 0, i32 1
  %"payload_e" = load i64, i64* %"payload_ptr_e"
  %"e" = alloca i64
  store i64 %"payload_e", i64* %"e"
  br label %"match_body_1"
match_body_1:
  %".27" = bitcast [20 x i8]* @"str_8" to i8*
  %".28" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %"e_load" = load i64, i64* %"e"
  %".29" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".30", i64 %"e_load")
  %".31" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".31")
  br label %"match_end"
match_next_2:
  br label %"match_end"
match_end.1:
  %"Option_lit" = call i8* @"GC_malloc"(i64 16)
  %"Option_cast" = bitcast i8* %"Option_lit" to %"Option"*
  %"tag_ptr" = getelementptr %"Option", %"Option"* %"Option_cast", i32 0, i32 0
  store i32 0, i32* %"tag_ptr"
  %"payload_ptr_0" = getelementptr %"Option", %"Option"* %"Option_cast", i32 0, i32 1
  store i64 42, i64* %"payload_ptr_0"
  %"opt" = alloca %"Option"*
  store %"Option"* %"Option_cast", %"Option"** %"opt"
  %"opt_load" = load %"Option"*, %"Option"** %"opt"
  br label %"match_next_0.2"
match_next_0.1:
  br label %"match_test_0.1"
match_test_0.1:
  %"match_tag_ptr_0.1" = getelementptr %"Result", %"Result"* %"res2_load", i32 0, i32 0
  %"match_tag_0.1" = load i32, i32* %"match_tag_ptr_0.1"
  %"match_tag_eq_0.1" = icmp eq i32 %"match_tag_0.1", 0
  br i1 %"match_tag_eq_0.1", label %"match_bind_0.1", label %"match_next_1.1"
match_bind_0.1:
  %"payload_ptr_val.1" = getelementptr %"Result", %"Result"* %"res2_load", i32 0, i32 1
  %"payload_val.1" = load i64, i64* %"payload_ptr_val.1"
  %"val.1" = alloca i64
  store i64 %"payload_val.1", i64* %"val.1"
  br label %"match_body_0.1"
match_body_0.1:
  %".39" = bitcast [25 x i8]* @"str_13" to i8*
  %".40" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".40", i8* %".39")
  %"val_load.1" = load i64, i64* %"val.1"
  %".41" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".41")
  %".42" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".42", i64 %"val_load.1")
  %".43" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".43")
  br label %"match_end.1"
match_next_1.1:
  br label %"match_test_1.1"
match_test_1.1:
  %"match_tag_ptr_1.1" = getelementptr %"Result", %"Result"* %"res2_load", i32 0, i32 0
  %"match_tag_1.1" = load i32, i32* %"match_tag_ptr_1.1"
  %"match_tag_eq_1.1" = icmp eq i32 %"match_tag_1.1", 1
  br i1 %"match_tag_eq_1.1", label %"match_bind_1.1", label %"match_next_2.1"
match_bind_1.1:
  %"payload_ptr_e.1" = getelementptr %"Result", %"Result"* %"res2_load", i32 0, i32 1
  %"payload_e.1" = load i64, i64* %"payload_ptr_e.1"
  %"e.1" = alloca i64
  store i64 %"payload_e.1", i64* %"e.1"
  br label %"match_body_1.1"
match_body_1.1:
  %".49" = bitcast [20 x i8]* @"str_18" to i8*
  %".50" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".50", i8* %".49")
  %"e_load.1" = load i64, i64* %"e.1"
  %".51" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".51")
  %".52" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".52", i64 %"e_load.1")
  %".53" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".53")
  br label %"match_end.1"
match_next_2.1:
  br label %"match_end.1"
match_end.2:
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
match_next_0.2:
  br label %"match_test_0.2"
match_test_0.2:
  %"match_tag_ptr_0.2" = getelementptr %"Option", %"Option"* %"opt_load", i32 0, i32 0
  %"match_tag_0.2" = load i32, i32* %"match_tag_ptr_0.2"
  %"match_tag_eq_0.2" = icmp eq i32 %"match_tag_0.2", 0
  br i1 %"match_tag_eq_0.2", label %"match_bind_0.2", label %"match_next_1.2"
match_bind_0.2:
  %"payload_ptr_v" = getelementptr %"Option", %"Option"* %"opt_load", i32 0, i32 1
  %"payload_v" = load i64, i64* %"payload_ptr_v"
  %"v" = alloca i64
  store i64 %"payload_v", i64* %"v"
  br label %"match_body_0.2"
match_body_0.2:
  %".64" = bitcast [16 x i8]* @"str_23" to i8*
  %".65" = bitcast [3 x i8]* @"str_24" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".65", i8* %".64")
  %"v_load" = load i64, i64* %"v"
  %".66" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".66")
  %".67" = bitcast [4 x i8]* @"str_26" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".67", i64 %"v_load")
  %".68" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".68")
  br label %"match_end.2"
match_next_1.2:
  br label %"match_test_1.2"
match_test_1.2:
  %"match_tag_ptr_1.2" = getelementptr %"Option", %"Option"* %"opt_load", i32 0, i32 0
  %"match_tag_1.2" = load i32, i32* %"match_tag_ptr_1.2"
  %"match_tag_eq_1.2" = icmp eq i32 %"match_tag_1.2", 1
  br i1 %"match_tag_eq_1.2", label %"match_bind_1.2", label %"match_next_2.2"
match_bind_1.2:
  br label %"match_body_1.2"
match_body_1.2:
  %".73" = bitcast [19 x i8]* @"str_28" to i8*
  %".74" = bitcast [3 x i8]* @"str_29" to i8*
  %"print_call.11" = call i32 (i8*, ...) @"printf"(i8* %".74", i8* %".73")
  %".75" = bitcast [2 x i8]* @"str_30" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".75")
  br label %"match_end.2"
match_next_2.2:
  br label %"match_end.2"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [43 x i8] c"Testando Standard Prelude (Auto-import)...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [25 x i8] c"Divis\c3\a3o 1 bem-sucedida:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [20 x i8] c"Erro na divis\c3\a3o 1:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [25 x i8] c"Divis\c3\a3o 2 bem-sucedida:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [20 x i8] c"Erro na divis\c3\a3o 2:\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c"\0a\00"
@"str_23" = constant [16 x i8] c"Option cont\c3\a9m:\00"
@"str_24" = constant [3 x i8] c"%s\00"
@"str_25" = constant [2 x i8] c" \00"
@"str_26" = constant [4 x i8] c"%ld\00"
@"str_27" = constant [2 x i8] c"\0a\00"
@"str_28" = constant [19 x i8] c"Option est\c3\a1 vazio\00"
@"str_29" = constant [3 x i8] c"%s\00"
@"str_30" = constant [2 x i8] c"\0a\00"