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
  %".7" = bitcast [23 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"array_lit" = alloca [5 x i64]
  %"arr_el_0" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 0
  store i64 10, i64* %"arr_el_0"
  %"arr_el_1" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 1
  store i64 20, i64* %"arr_el_1"
  %"arr_el_2" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 2
  store i64 30, i64* %"arr_el_2"
  %"arr_el_3" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 3
  store i64 40, i64* %"arr_el_3"
  %"arr_el_4" = getelementptr [5 x i64], [5 x i64]* %"array_lit", i32 0, i32 4
  store i64 50, i64* %"arr_el_4"
  %"numeros" = alloca i64*
  %"ptr_cast" = bitcast [5 x i64]* %"array_lit" to i64*
  store i64* %"ptr_cast", i64** %"numeros"
  %".16" = bitcast [16 x i8]* @"str_3" to i8*
  %".17" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".17", i8* %".16")
  %".18" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %"numeros_load" = load i64*, i64** %"numeros"
  %"__for_idx_num" = alloca i64
  store i64 0, i64* %"__for_idx_num"
  %"num" = alloca i64
  br label %"forin_cond"
forin_cond:
  %"forin_cur" = load i64, i64* %"__for_idx_num"
  %"forin_cond.1" = icmp slt i64 %"forin_cur", 5
  br i1 %"forin_cond.1", label %"forin_body", label %"forin_end"
forin_body:
  %"forin_ep" = getelementptr i64, i64* %"numeros_load", i64 %"forin_cur"
  %"forin_elem" = load i64, i64* %"forin_ep"
  store i64 %"forin_elem", i64* %"num"
  %".23" = bitcast [7 x i8]* @"str_6" to i8*
  %".24" = bitcast [3 x i8]* @"str_7" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".24", i8* %".23")
  %"num_load" = load i64, i64* %"num"
  %".25" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".25")
  %".26" = bitcast [4 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".26", i64 %"num_load")
  %".27" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".27")
  br label %"forin_inc"
forin_inc:
  %"forin_cur_inc" = load i64, i64* %"__for_idx_num"
  %"forin_next" = add i64 %"forin_cur_inc", 1
  store i64 %"forin_next", i64* %"__for_idx_num"
  br label %"forin_cond"
forin_end:
  %".31" = bitcast [7 x i8]* @"str_11" to i8*
  %"texto" = alloca i8*
  store i8* %".31", i8** %"texto"
  %".33" = bitcast [17 x i8]* @"str_12" to i8*
  %".34" = bitcast [3 x i8]* @"str_13" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".34", i8* %".33")
  %".35" = bitcast [2 x i8]* @"str_14" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".35")
  %"texto_load" = load i8*, i8** %"texto"
  %"forin_strlen" = call i64 @"strlen"(i8* %"texto_load")
  %"__for_idx_c" = alloca i64
  store i64 0, i64* %"__for_idx_c"
  %"c" = alloca i8
  br label %"forin_cond.2"
forin_cond.2:
  %"forin_cur.1" = load i64, i64* %"__for_idx_c"
  %"forin_cond.3" = icmp slt i64 %"forin_cur.1", %"forin_strlen"
  br i1 %"forin_cond.3", label %"forin_body.1", label %"forin_end.1"
forin_body.1:
  %"forin_ep.1" = getelementptr i8, i8* %"texto_load", i64 %"forin_cur.1"
  %"forin_elem.1" = load i8, i8* %"forin_ep.1"
  %"forin_sext" = sext i8 %"forin_elem.1" to i64
  %"forin_trunc" = trunc i64 %"forin_sext" to i8
  store i8 %"forin_trunc", i8* %"c"
  %".40" = bitcast [12 x i8]* @"str_15" to i8*
  %".41" = bitcast [3 x i8]* @"str_16" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".41", i8* %".40")
  %"c_load" = load i8, i8* %"c"
  %".42" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".42")
  %"print_zext" = zext i8 %"c_load" to i64
  %".43" = bitcast [4 x i8]* @"str_18" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".43", i64 %"print_zext")
  %".44" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".44")
  br label %"forin_inc.1"
forin_inc.1:
  %"forin_cur_inc.1" = load i64, i64* %"__for_idx_c"
  %"forin_next.1" = add i64 %"forin_cur_inc.1", 1
  store i64 %"forin_next.1", i64* %"__for_idx_c"
  br label %"forin_cond.2"
forin_end.1:
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [23 x i8] c"Testando Iteradores...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [16 x i8] c"Iterando Array:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c"\0a\00"
@"str_6" = constant [7 x i8] c"Valor:\00"
@"str_7" = constant [3 x i8] c"%s\00"
@"str_8" = constant [2 x i8] c" \00"
@"str_9" = constant [4 x i8] c"%ld\00"
@"str_10" = constant [2 x i8] c"\0a\00"
@"str_11" = constant [7 x i8] c"Lumina\00"
@"str_12" = constant [17 x i8] c"Iterando String:\00"
@"str_13" = constant [3 x i8] c"%s\00"
@"str_14" = constant [2 x i8] c"\0a\00"
@"str_15" = constant [12 x i8] c"Char ASCII:\00"
@"str_16" = constant [3 x i8] c"%s\00"
@"str_17" = constant [2 x i8] c" \00"
@"str_18" = constant [4 x i8] c"%ld\00"
@"str_19" = constant [2 x i8] c"\0a\00"