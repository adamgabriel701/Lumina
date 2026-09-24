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
declare i64 @"clock"()

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

define i64 @"dividir"(i64 %".1", i64 %".2")
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
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"a_load" = load i64, i64* %"a"
  %"b_load.1" = load i64, i64* %"b"
  %"div" = sdiv i64 %"a_load", %"b_load.1"
  ret i64 %"div"
}

define i64 @"main"()
{
main_entry:
  call void @"GC_init"()
  br label %"main_body"
main_body:
  %"limit_str" = alloca i8*
  %"int_to_str_buf" = alloca [32 x i8]
  %"int_str_ptr" = bitcast [32 x i8]* %"int_to_str_buf" to i8*
  %".3" = bitcast [4 x i8]* @"str_0" to i8*
  %"int_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"int_str_ptr", i64 32, i8* %".3", i64 0)
  store i8* %"int_str_ptr", i8** %"limit_str"
  %"limit" = alloca i64
  store i64 10000000, i64* %"limit"
  %"limit_str_load" = load i8*, i8** %"limit_str"
  %"len_str" = call i64 @"strlen"(i8* %"limit_str_load")
  %"icmp" = icmp sgt i64 %"len_str", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"limit_str_load.1" = load i8*, i8** %"limit_str"
  %"atoi_call" = call i64 @"atoi"(i8* %"limit_str_load.1")
  store i64 %"atoi_call", i64* %"limit"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"clock_call" = call i64 @"clock"()
  %"start" = alloca i64
  store i64 %"clock_call", i64* %"start"
  %"x" = alloca i64
  store i64 0, i64* %"x"
  %"limit_load" = load i64, i64* %"limit"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", %"limit_load"
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"x_load" = load i64, i64* %"x"
  %"i_load" = load i64, i64* %"i"
  %"add" = add i64 %"x_load", %"i_load"
  store i64 %"add", i64* %"x"
  br label %"for_inc"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %".19" = bitcast [11 x i8]* @"str_1" to i8*
  %".20" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %"x_load.1" = load i64, i64* %"x"
  %".21" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [4 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".22", i64 %"x_load.1")
  %".23" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %"clock_call.1" = call i64 @"clock"()
  %"end" = alloca i64
  store i64 %"clock_call.1", i64* %"end"
  %"end_load" = load i64, i64* %"end"
  %"start_load" = load i64, i64* %"start"
  %"sub" = sub i64 %"end_load", %"start_load"
  %"diff" = alloca i64
  store i64 %"sub", i64* %"diff"
  %"diff_load" = load i64, i64* %"diff"
  %"int_to_float" = sitofp i64 %"diff_load" to double
  %"diff_f" = alloca i64
  %"float_to_int_store" = fptosi double %"int_to_float" to i64
  store i64 %"float_to_int_store", i64* %"diff_f"
  %"diff_f_load" = load i64, i64* %"diff_f"
  %"int_to_float.1" = sitofp i64 %"diff_f_load" to double
  %"fdiv" = fdiv double %"int_to_float.1", 0x412e848000000000
  %"sec" = alloca double
  store double %"fdiv", double* %"sec"
  %".28" = bitcast [16 x i8]* @"str_6" to i8*
  %".29" = bitcast [3 x i8]* @"str_7" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".29", i8* %".28")
  %"sec_load" = load double, double* %"sec"
  %".30" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %".31" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".31", double %"sec_load")
  %".32" = bitcast [9 x i8]* @"str_10" to i8*
  %".33" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".33")
  %".34" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".34", i8* %".32")
  %".35" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".35")
  ret i64 0
}

@"str_0" = constant [4 x i8] c"%ld\00"
@"str_1" = constant [11 x i8] c"Resultado:\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c" \00"
@"str_4" = constant [4 x i8] c"%ld\00"
@"str_5" = constant [2 x i8] c"\0a\00"
@"str_6" = constant [16 x i8] c"Lumina Runtime:\00"
@"str_7" = constant [3 x i8] c"%s\00"
@"str_8" = constant [2 x i8] c" \00"
@"str_9" = constant [3 x i8] c"%f\00"
@"str_10" = constant [9 x i8] c"segundos\00"
@"str_11" = constant [2 x i8] c" \00"
@"str_12" = constant [3 x i8] c"%s\00"
@"str_13" = constant [2 x i8] c"\0a\00"