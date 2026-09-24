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
  %"alloc_size" = mul i64 10, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"arr" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"arr"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", 10
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"i_load" = load i64, i64* %"i"
  %"mul" = mul i64 %"i_load", 5
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load", i64 %"i_load.1"
  store i64 %"mul", i64* %"idx_ptr"
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %"alvo" = alloca i64
  store i64 25, i64* %"alvo"
  %"neg" = sub i64 0, 1
  %"indice_encontrado" = alloca i64
  store i64 %"neg", i64* %"indice_encontrado"
  %"i.1" = alloca i64
  store i64 0, i64* %"i.1"
  br label %"for_cond.2"
for_cond.2:
  %"for_curr.1" = load i64, i64* %"i.1"
  %"for_cond.3" = icmp slt i64 %"for_curr.1", 10
  br i1 %"for_cond.3", label %"for_body.1", label %"for_end.1"
for_body.1:
  %"arr_load.1" = load i64*, i64** %"arr"
  %"i_load.2" = load i64, i64* %"i.1"
  %".20" = getelementptr i64, i64* %"arr_load.1", i64 %"i_load.2"
  %"ptr_idx_load" = load i64, i64* %".20"
  %"alvo_load" = load i64, i64* %"alvo"
  %"icmp" = icmp eq i64 %"ptr_idx_load", %"alvo_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
for_inc.1:
  %"for_curr_inc.1" = load i64, i64* %"i.1"
  %"for_next.1" = add i64 %"for_curr_inc.1", 1
  store i64 %"for_next.1", i64* %"i.1"
  br label %"for_cond.2"
for_end.1:
  %"indice_encontrado_load" = load i64, i64* %"indice_encontrado"
  %"neg.1" = sub i64 0, 1
  %"icmp.1" = icmp ne i64 %"indice_encontrado_load", %"neg.1"
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then:
  %"i_load.3" = load i64, i64* %"i.1"
  store i64 %"i_load.3", i64* %"indice_encontrado"
  br label %"for_end.1"
if_else:
  br label %"if_end"
if_end:
  br label %"for_inc.1"
if_then.1:
  %".29" = bitcast [7 x i8]* @"str_0" to i8*
  %".30" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".29")
  %"alvo_load.1" = load i64, i64* %"alvo"
  %".31" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".32", i64 %"alvo_load.1")
  %".33" = bitcast [22 x i8]* @"str_4" to i8*
  %".34" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".34")
  %".35" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".35", i8* %".33")
  %"indice_encontrado_load.1" = load i64, i64* %"indice_encontrado"
  %".36" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %".37" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".37", i64 %"indice_encontrado_load.1")
  %".38" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".38")
  br label %"if_end.1"
if_else.1:
  %".40" = bitcast [23 x i8]* @"str_10" to i8*
  %".41" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".41", i8* %".40")
  %".42" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".42")
  br label %"if_end.1"
if_end.1:
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [7 x i8] c"Numero\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [22 x i8] c"encontrado no indice:\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [23 x i8] c"Numero nao encontrado.\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c"\0a\00"