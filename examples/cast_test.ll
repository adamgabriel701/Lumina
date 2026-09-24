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
  %".7" = bitcast [34 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"inteiro" = alloca i64
  store i64 10, i64* %"inteiro"
  %"flutuante" = alloca double
  store double 0x40091eb851eb851f, double* %"flutuante"
  %"inteiro_load" = load i64, i64* %"inteiro"
  %"int_to_float" = sitofp i64 %"inteiro_load" to double
  %"x" = alloca i64
  %"float_to_int_store" = fptosi double %"int_to_float" to i64
  store i64 %"float_to_int_store", i64* %"x"
  %".13" = bitcast [14 x i8]* @"str_3" to i8*
  %".14" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %"x_load" = load i64, i64* %"x"
  %".15" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".16", i64 %"x_load")
  %".17" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %"flutuante_load" = load double, double* %"flutuante"
  %"float_to_int" = fptosi double %"flutuante_load" to i64
  %"y" = alloca i64
  store i64 %"float_to_int", i64* %"y"
  %".19" = bitcast [14 x i8]* @"str_8" to i8*
  %".20" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %"y_load" = load i64, i64* %"y"
  %".21" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".22", i64 %"y_load")
  %".23" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %"inteiro_load.1" = load i64, i64* %"inteiro"
  %"add" = add i64 %"inteiro_load.1", 5
  %"int_to_float.1" = sitofp i64 %"add" to double
  %"z" = alloca i64
  %"float_to_int_store.1" = fptosi double %"int_to_float.1" to i64
  store i64 %"float_to_int_store.1", i64* %"z"
  %".25" = bitcast [15 x i8]* @"str_13" to i8*
  %".26" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".26", i8* %".25")
  %"z_load" = load i64, i64* %"z"
  %".27" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".27")
  %".28" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".28", i64 %"z_load")
  %".29" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %"arr_stack" = alloca [10 x i64]
  %"arr_first" = getelementptr [10 x i64], [10 x i64]* %"arr_stack", i32 0, i32 0
  %"arr" = alloca i64*
  store i64* %"arr_first", i64** %"arr"
  %"arr_load" = load i64*, i64** %"arr"
  %"ptr_to_int" = ptrtoint i64* %"arr_load" to i64
  %"ptr_val" = alloca i64
  store i64 %"ptr_to_int", i64* %"ptr_val"
  %".32" = bitcast [12 x i8]* @"str_18" to i8*
  %".33" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %".32")
  %"ptr_val_load" = load i64, i64* %"ptr_val"
  %".34" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".34")
  %".35" = bitcast [4 x i8]* @"str_21" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".35", i64 %"ptr_val_load")
  %".36" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [34 x i8] c"Testando Casting de Tipos (as)...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [14 x i8] c"Int -> Float:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [14 x i8] c"Float -> Int:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [15 x i8] c"Expr -> Float:\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [12 x i8] c"Ptr -> Int:\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c"\0a\00"