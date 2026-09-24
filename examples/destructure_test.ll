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
define i64* @"obter_coordenadas"()
{
obter_coordenadas_entry:
  br label %"obter_coordenadas_body"
obter_coordenadas_body:
  %"alloc_size" = mul i64 2, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"arr" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"arr"
  %"arr_load" = load i64*, i64** %"arr"
  %"idx_ptr" = getelementptr i64, i64* %"arr_load", i64 0
  store i64 42, i64* %"idx_ptr"
  %"arr_load.1" = load i64*, i64** %"arr"
  %"idx_ptr.1" = getelementptr i64, i64* %"arr_load.1", i64 1
  store i64 99, i64* %"idx_ptr.1"
  %"arr_load.2" = load i64*, i64** %"arr"
  ret i64* %"arr_load.2"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [26 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"obter_coordenadas_call" = call i64* @"obter_coordenadas"()
  %"x_ptr" = getelementptr i64, i64* %"obter_coordenadas_call", i64 0
  %"x" = load i64, i64* %"x_ptr"
  %"x.1" = alloca i64
  store i64 %"x", i64* %"x.1"
  %"y_ptr" = getelementptr i64, i64* %"obter_coordenadas_call", i64 1
  %"y" = load i64, i64* %"y_ptr"
  %"y.1" = alloca i64
  store i64 %"y", i64* %"y.1"
  %".12" = bitcast [3 x i8]* @"str_3" to i8*
  %".13" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %".12")
  %"x_load" = load i64, i64* %"x.1"
  %".14" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"x_load")
  %".16" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [3 x i8]* @"str_8" to i8*
  %".18" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"y_load" = load i64, i64* %"y.1"
  %".19" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".19")
  %".20" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".20", i64 %"y_load")
  %".21" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %"alloc_size" = mul i64 3, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"dados" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"dados"
  %"dados_load" = load i64*, i64** %"dados"
  %"idx_ptr" = getelementptr i64, i64* %"dados_load", i64 0
  store i64 10, i64* %"idx_ptr"
  %"dados_load.1" = load i64*, i64** %"dados"
  %"idx_ptr.1" = getelementptr i64, i64* %"dados_load.1", i64 1
  store i64 20, i64* %"idx_ptr.1"
  %"dados_load.2" = load i64*, i64** %"dados"
  %"idx_ptr.2" = getelementptr i64, i64* %"dados_load.2", i64 2
  store i64 30, i64* %"idx_ptr.2"
  %"dados_load.3" = load i64*, i64** %"dados"
  %"a_ptr" = getelementptr i64, i64* %"dados_load.3", i64 0
  %"a" = load i64, i64* %"a_ptr"
  %"a.1" = alloca i64
  store i64 %"a", i64* %"a.1"
  %"b_ptr" = getelementptr i64, i64* %"dados_load.3", i64 1
  %"b" = load i64, i64* %"b_ptr"
  %"b.1" = alloca i64
  store i64 %"b", i64* %"b.1"
  %"c_ptr" = getelementptr i64, i64* %"dados_load.3", i64 2
  %"c" = load i64, i64* %"c_ptr"
  %"c.1" = alloca i64
  store i64 %"c", i64* %"c.1"
  %".29" = bitcast [3 x i8]* @"str_13" to i8*
  %".30" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".29")
  %"a_load" = load i64, i64* %"a.1"
  %".31" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".32", i64 %"a_load")
  %".33" = bitcast [3 x i8]* @"str_17" to i8*
  %".34" = bitcast [2 x i8]* @"str_18" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".34")
  %".35" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".35", i8* %".33")
  %"b_load" = load i64, i64* %"b.1"
  %".36" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %".37" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".37", i64 %"b_load")
  %".38" = bitcast [3 x i8]* @"str_22" to i8*
  %".39" = bitcast [2 x i8]* @"str_23" to i8*
  %"print_sep.5" = call i32 (i8*, ...) @"printf"(i8* %".39")
  %".40" = bitcast [3 x i8]* @"str_24" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".40", i8* %".38")
  %"c_load" = load i64, i64* %"c.1"
  %".41" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_sep.6" = call i32 (i8*, ...) @"printf"(i8* %".41")
  %".42" = bitcast [4 x i8]* @"str_26" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".42", i64 %"c_load")
  %".43" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".43")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [26 x i8] c"Testando Destructuring...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [3 x i8] c"X:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [3 x i8] c"Y:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [3 x i8] c"A:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [3 x i8] c"B:\00"
@"str_18" = constant [2 x i8] c" \00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [3 x i8] c"C:\00"
@"str_23" = constant [2 x i8] c" \00"
@"str_24" = constant [3 x i8] c"%s\00"
@"str_25" = constant [2 x i8] c" \00"
@"str_26" = constant [4 x i8] c"%ld\00"
@"str_27" = constant [2 x i8] c"\0a\00"