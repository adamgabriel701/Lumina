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
define i64 @"avaliar"(i64 %".1")
{
avaliar_entry:
  %"n" = alloca i64
  store i64 %".1", i64* %"n"
  br label %"avaliar_body"
avaliar_body:
  %"n_load" = load i64, i64* %"n"
  switch i64 %"n_load", label %"match_default" [i64 1, label %"match_case" i64 2, label %"match_case.1" i64 3, label %"match_case.2"]
match_end:
  %"match_res" = phi  i64 [100, %"match_case"], [200, %"match_case.1"], [300, %"match_case.2"], [999, %"match_default"]
  ret i64 %"match_res"
match_default:
  br label %"match_end"
match_case:
  br label %"match_end"
match_case.1:
  br label %"match_end"
match_case.2:
  br label %"match_end"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [30 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"avaliar_call" = call i64 @"avaliar"(i64 1)
  %"r1" = alloca i64
  store i64 %"avaliar_call", i64* %"r1"
  %"avaliar_call.1" = call i64 @"avaliar"(i64 2)
  %"r2" = alloca i64
  store i64 %"avaliar_call.1", i64* %"r2"
  %"avaliar_call.2" = call i64 @"avaliar"(i64 3)
  %"r3" = alloca i64
  store i64 %"avaliar_call.2", i64* %"r3"
  %"avaliar_call.3" = call i64 @"avaliar"(i64 10)
  %"r4" = alloca i64
  store i64 %"avaliar_call.3", i64* %"r4"
  %".14" = bitcast [11 x i8]* @"str_3" to i8*
  %".15" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".15", i8* %".14")
  %"r1_load" = load i64, i64* %"r1"
  %".16" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".17", i64 %"r1_load")
  %".18" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %".19" = bitcast [11 x i8]* @"str_8" to i8*
  %".20" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %"r2_load" = load i64, i64* %"r2"
  %".21" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".22", i64 %"r2_load")
  %".23" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %".24" = bitcast [11 x i8]* @"str_13" to i8*
  %".25" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %".24")
  %"r3_load" = load i64, i64* %"r3"
  %".26" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".27", i64 %"r3_load")
  %".28" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".28")
  %".29" = bitcast [12 x i8]* @"str_18" to i8*
  %".30" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".29")
  %"r4_load" = load i64, i64* %"r4"
  %".31" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".32", i64 %"r4_load")
  %".33" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".33")
  %".34" = bitcast [8 x i8]* @"str_23" to i8*
  %".35" = bitcast [3 x i8]* @"str_24" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".35", i8* %".34")
  switch i64 2, label %"match_default" [i64 1, label %"match_case" i64 2, label %"match_case.1"]
match_end:
  %"match_res" = phi  i64 [10, %"match_case"], [20, %"match_case.1"], [0, %"match_default"]
  %".40" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".40")
  %".41" = bitcast [4 x i8]* @"str_26" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".41", i64 %"match_res")
  %".42" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".42")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
match_default:
  br label %"match_end"
match_case:
  br label %"match_end"
match_case.1:
  br label %"match_end"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [30 x i8] c"Testando Match Expressions...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [11 x i8] c"Avaliar 1:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [11 x i8] c"Avaliar 2:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [11 x i8] c"Avaliar 3:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [12 x i8] c"Avaliar 10:\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c"\0a\00"
@"str_23" = constant [8 x i8] c"Inline:\00"
@"str_24" = constant [3 x i8] c"%s\00"
@"str_25" = constant [2 x i8] c" \00"
@"str_26" = constant [4 x i8] c"%ld\00"
@"str_27" = constant [2 x i8] c"\0a\00"