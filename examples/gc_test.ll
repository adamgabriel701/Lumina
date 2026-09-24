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
declare i64 @"usleep"(i64 %".1")

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
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 1000000
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %".13" = bitcast [24 x i8]* @"str_3" to i8*
  %"i_load.1" = load i64, i64* %"i"
  %".14" = bitcast [4 x i8]* @"str_4" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".14", i64 %"i_load.1")
  %"sconcat_len1" = call i64 @"strlen"(i8* %".13")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".13")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"num_to_str_ptr")
  %"lixo" = alloca i8*
  store i8* %"sconcat_buf", i8** %"lixo"
  %"i_load.2" = load i64, i64* %"i"
  %"mod" = srem i64 %"i_load.2", 100000
  %"icmp.1" = icmp eq i64 %"mod", 0
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %".29" = bitcast [48 x i8]* @"str_13" to i8*
  %".30" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".29")
  %".31" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
if_then:
  %".17" = bitcast [19 x i8]* @"str_5" to i8*
  %".18" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"i_load.3" = load i64, i64* %"i"
  %".19" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".20", i64 %"i_load.3")
  %".21" = bitcast [11 x i8]* @"str_9" to i8*
  %".22" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %".23" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".21")
  %".24" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".24")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.4" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.4", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [43 x i8] c"Testando o Garbage Collector (Boehm GC)...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [24 x i8] c"Lixo da memoria numero \00"
@"str_4" = constant [4 x i8] c"%ld\00"
@"str_5" = constant [19 x i8] c"Alocou e descartou\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [11 x i8] c"strings...\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [48 x i8] c"Memoria limpa automaticamente! O PC nao travou.\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c"\0a\00"