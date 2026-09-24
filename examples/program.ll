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
  %".7" = bitcast [29 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"base" = alloca double
  store double 0x4000000000000000, double* %"base"
  %"exp" = alloca double
  store double 0x4024000000000000, double* %"exp"
  %"base_load" = load double, double* %"base"
  %"exp_load" = load double, double* %"exp"
  %"potencia_call" = call double @"potencia"(double %"base_load", double %"exp_load")
  %"res" = alloca double
  store double %"potencia_call", double* %"res"
  %".13" = bitcast [19 x i8]* @"str_3" to i8*
  %".14" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %"res_load" = load double, double* %"res"
  %".15" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".16", double %"res_load")
  %".17" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %"raiz_quadrada_call" = call double @"raiz_quadrada"(double 0x4062000000000000)
  %"raiz" = alloca double
  store double %"raiz_quadrada_call", double* %"raiz"
  %".19" = bitcast [16 x i8]* @"str_8" to i8*
  %".20" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %"raiz_load" = load double, double* %"raiz"
  %".21" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".22", double %"raiz_load")
  %".23" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %".24" = bitcast [22 x i8]* @"str_13" to i8*
  %".25" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %".24")
  %".26" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [10 x i8]* @"str_16" to i8*
  %".28" = bitcast [20 x i8]* @"str_17" to i8*
  %".29" = bitcast [2 x i8]* @"str_18" to i8*
  %"wf_fopen" = call i8* @"fopen"(i8* %".27", i8* %".29")
  %"wf_fputs" = call i32 @"fputs"(i8* %".28", i8* %"wf_fopen")
  %"wf_fclose" = call i32 @"fclose"(i8* %"wf_fopen")
  %".30" = bitcast [23 x i8]* @"str_19" to i8*
  %".31" = bitcast [3 x i8]* @"str_20" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".31", i8* %".30")
  %".32" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".32")
  %".33" = bitcast [10 x i8]* @"str_22" to i8*
  %"deletar_arquivo_call" = call i64 @"deletar_arquivo"(i8* %".33")
  %"ret" = alloca i64
  store i64 %"deletar_arquivo_call", i64* %"ret"
  %".35" = bitcast [30 x i8]* @"str_23" to i8*
  %".36" = bitcast [3 x i8]* @"str_24" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".36", i8* %".35")
  %"ret_load" = load i64, i64* %"ret"
  %".37" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".37")
  %".38" = bitcast [4 x i8]* @"str_26" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".38", i64 %"ret_load")
  %".39" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".39")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
declare double @"pow"(double %".1", double %".2")

declare double @"sqrt"(double %".1")

declare double @"fabs"(double %".1")

declare double @"floor"(double %".1")

declare double @"ceil"(double %".1")

declare double @"round"(double %".1")

declare i64 @"abs"(i64 %".1")

declare i64 @"rand"()

declare void @"srand"(i64 %".1")

define double @"potencia"(double %".1", double %".2")
{
potencia_entry:
  %"base" = alloca double
  store double %".1", double* %"base"
  %"exp" = alloca double
  store double %".2", double* %"exp"
  br label %"potencia_body"
potencia_body:
  %"base_load" = load double, double* %"base"
  %"exp_load" = load double, double* %"exp"
  %"pow_call" = call double @"pow"(double %"base_load", double %"exp_load")
  ret double %"pow_call"
}

define double @"raiz_quadrada"(double %".1")
{
raiz_quadrada_entry:
  %"val" = alloca double
  store double %".1", double* %"val"
  br label %"raiz_quadrada_body"
raiz_quadrada_body:
  %"val_load" = load double, double* %"val"
  %"sqrt_call" = call double @"sqrt"(double %"val_load")
  ret double %"sqrt_call"
}

define i64 @"valor_absoluto"(i64 %".1")
{
valor_absoluto_entry:
  %"val" = alloca i64
  store i64 %".1", i64* %"val"
  br label %"valor_absoluto_body"
valor_absoluto_body:
  %"val_load" = load i64, i64* %"val"
  %"abs_call" = call i64 @"abs"(i64 %"val_load")
  ret i64 %"abs_call"
}

define double @"chao"(double %".1")
{
chao_entry:
  %"val" = alloca double
  store double %".1", double* %"val"
  br label %"chao_body"
chao_body:
  %"val_load" = load double, double* %"val"
  %"floor_call" = call double @"floor"(double %"val_load")
  ret double %"floor_call"
}

define double @"teto"(double %".1")
{
teto_entry:
  %"val" = alloca double
  store double %".1", double* %"val"
  br label %"teto_body"
teto_body:
  %"val_load" = load double, double* %"val"
  %"ceil_call" = call double @"ceil"(double %"val_load")
  ret double %"ceil_call"
}

define double @"arredondar"(double %".1")
{
arredondar_entry:
  %"val" = alloca double
  store double %".1", double* %"val"
  br label %"arredondar_body"
arredondar_body:
  %"val_load" = load double, double* %"val"
  %"round_call" = call double @"round"(double %"val_load")
  ret double %"round_call"
}

define double @"abs_float"(double %".1")
{
abs_float_entry:
  %"val" = alloca double
  store double %".1", double* %"val"
  br label %"abs_float_body"
abs_float_body:
  %"val_load" = load double, double* %"val"
  %"fabs_call" = call double @"fabs"(double %"val_load")
  ret double %"fabs_call"
}

define i64 @"min"(i64 %".1", i64 %".2")
{
min_entry:
  %"a" = alloca i64
  store i64 %".1", i64* %"a"
  %"b" = alloca i64
  store i64 %".2", i64* %"b"
  br label %"min_body"
min_body:
  %"a_load" = load i64, i64* %"a"
  %"b_load" = load i64, i64* %"b"
  %"icmp" = icmp slt i64 %"a_load", %"b_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"a_load.1" = load i64, i64* %"a"
  ret i64 %"a_load.1"
if_else:
  br label %"if_end"
if_end:
  %"b_load.1" = load i64, i64* %"b"
  ret i64 %"b_load.1"
}

define i64 @"max"(i64 %".1", i64 %".2")
{
max_entry:
  %"a" = alloca i64
  store i64 %".1", i64* %"a"
  %"b" = alloca i64
  store i64 %".2", i64* %"b"
  br label %"max_body"
max_body:
  %"a_load" = load i64, i64* %"a"
  %"b_load" = load i64, i64* %"b"
  %"icmp" = icmp sgt i64 %"a_load", %"b_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"a_load.1" = load i64, i64* %"a"
  ret i64 %"a_load.1"
if_else:
  br label %"if_end"
if_end:
  %"b_load.1" = load i64, i64* %"b"
  ret i64 %"b_load.1"
}

define i64 @"clamp"(i64 %".1", i64 %".2", i64 %".3")
{
clamp_entry:
  %"v" = alloca i64
  store i64 %".1", i64* %"v"
  %"lo" = alloca i64
  store i64 %".2", i64* %"lo"
  %"hi" = alloca i64
  store i64 %".3", i64* %"hi"
  br label %"clamp_body"
clamp_body:
  %"v_load" = load i64, i64* %"v"
  %"lo_load" = load i64, i64* %"lo"
  %"icmp" = icmp slt i64 %"v_load", %"lo_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"lo_load.1" = load i64, i64* %"lo"
  ret i64 %"lo_load.1"
if_else:
  br label %"if_end"
if_end:
  %"v_load.1" = load i64, i64* %"v"
  %"hi_load" = load i64, i64* %"hi"
  %"icmp.1" = icmp sgt i64 %"v_load.1", %"hi_load"
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"hi_load.1" = load i64, i64* %"hi"
  ret i64 %"hi_load.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"v_load.2" = load i64, i64* %"v"
  ret i64 %"v_load.2"
}

define i64 @"gcd"(i64 %".1", i64 %".2")
{
gcd_entry:
  %"a" = alloca i64
  store i64 %".1", i64* %"a"
  %"b" = alloca i64
  store i64 %".2", i64* %"b"
  br label %"gcd_body"
gcd_body:
  %"a_load" = load i64, i64* %"a"
  %"x" = alloca i64
  store i64 %"a_load", i64* %"x"
  %"b_load" = load i64, i64* %"b"
  %"y" = alloca i64
  store i64 %"b_load", i64* %"y"
  %"x_load" = load i64, i64* %"x"
  %"icmp" = icmp slt i64 %"x_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"x_load.1" = load i64, i64* %"x"
  %"neg" = sub i64 0, %"x_load.1"
  store i64 %"neg", i64* %"x"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"y_load" = load i64, i64* %"y"
  %"icmp.1" = icmp slt i64 %"y_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"y_load.1" = load i64, i64* %"y"
  %"neg.1" = sub i64 0, %"y_load.1"
  store i64 %"neg.1", i64* %"y"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  br label %"while_cond"
while_cond:
  %"y_load.2" = load i64, i64* %"y"
  %"icmp.2" = icmp ne i64 %"y_load.2", 0
  br i1 %"icmp.2", label %"while_body", label %"while_end"
while_body:
  %"y_load.3" = load i64, i64* %"y"
  %"t" = alloca i64
  store i64 %"y_load.3", i64* %"t"
  %"x_load.2" = load i64, i64* %"x"
  %"y_load.4" = load i64, i64* %"y"
  %"mod" = srem i64 %"x_load.2", %"y_load.4"
  store i64 %"mod", i64* %"y"
  %"t_load" = load i64, i64* %"t"
  store i64 %"t_load", i64* %"x"
  br label %"while_cond"
while_end:
  %"x_load.3" = load i64, i64* %"x"
  ret i64 %"x_load.3"
}

define i64 @"lcm"(i64 %".1", i64 %".2")
{
lcm_entry:
  %"a" = alloca i64
  store i64 %".1", i64* %"a"
  %"b" = alloca i64
  store i64 %".2", i64* %"b"
  br label %"lcm_body"
lcm_body:
  %"a_load" = load i64, i64* %"a"
  %"icmp" = icmp eq i64 %"a_load", 0
  br i1 %"icmp", label %"or_end", label %"or_rhs"
or_rhs:
  %"b_load" = load i64, i64* %"b"
  %"icmp.1" = icmp eq i64 %"b_load", 0
  br label %"or_end"
or_end:
  %"or_result" = phi  i1 [1, %"lcm_body"], [%"icmp.1", %"or_rhs"]
  br i1 %"or_result", label %"if_then", label %"if_else"
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"a_load.1" = load i64, i64* %"a"
  %"b_load.1" = load i64, i64* %"b"
  %"gcd_call" = call i64 @"gcd"(i64 %"a_load.1", i64 %"b_load.1")
  %"g" = alloca i64
  store i64 %"gcd_call", i64* %"g"
  %"a_load.2" = load i64, i64* %"a"
  %"g_load" = load i64, i64* %"g"
  %"div" = sdiv i64 %"a_load.2", %"g_load"
  %"prod" = alloca i64
  store i64 %"div", i64* %"prod"
  %"prod_load" = load i64, i64* %"prod"
  %"icmp.2" = icmp slt i64 %"prod_load", 0
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"prod_load.1" = load i64, i64* %"prod"
  %"neg" = sub i64 0, %"prod_load.1"
  store i64 %"neg", i64* %"prod"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"b_load.2" = load i64, i64* %"b"
  %"bb" = alloca i64
  store i64 %"b_load.2", i64* %"bb"
  %"bb_load" = load i64, i64* %"bb"
  %"icmp.3" = icmp slt i64 %"bb_load", 0
  br i1 %"icmp.3", label %"if_then.2", label %"if_else.2"
if_then.2:
  %"bb_load.1" = load i64, i64* %"bb"
  %"neg.1" = sub i64 0, %"bb_load.1"
  store i64 %"neg.1", i64* %"bb"
  br label %"if_end.2"
if_else.2:
  br label %"if_end.2"
if_end.2:
  %"prod_load.2" = load i64, i64* %"prod"
  %"bb_load.2" = load i64, i64* %"bb"
  %"mul" = mul i64 %"prod_load.2", %"bb_load.2"
  ret i64 %"mul"
}

define i64 @"powi"(i64 %".1", i64 %".2")
{
powi_entry:
  %"base" = alloca i64
  store i64 %".1", i64* %"base"
  %"exp" = alloca i64
  store i64 %".2", i64* %"exp"
  br label %"powi_body"
powi_body:
  %"exp_load" = load i64, i64* %"exp"
  %"icmp" = icmp slt i64 %"exp_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"result" = alloca i64
  store i64 1, i64* %"result"
  %"base_load" = load i64, i64* %"base"
  %"b" = alloca i64
  store i64 %"base_load", i64* %"b"
  %"exp_load.1" = load i64, i64* %"exp"
  %"e" = alloca i64
  store i64 %"exp_load.1", i64* %"e"
  br label %"while_cond"
while_cond:
  %"e_load" = load i64, i64* %"e"
  %"icmp.1" = icmp sgt i64 %"e_load", 0
  br i1 %"icmp.1", label %"while_body", label %"while_end"
while_body:
  %"e_load.1" = load i64, i64* %"e"
  %"bitand" = and i64 %"e_load.1", 1
  %"icmp.2" = icmp eq i64 %"bitand", 1
  br i1 %"icmp.2", label %"if_then.1", label %"if_else.1"
while_end:
  %"result_load.1" = load i64, i64* %"result"
  ret i64 %"result_load.1"
if_then.1:
  %"result_load" = load i64, i64* %"result"
  %"b_load" = load i64, i64* %"b"
  %"mul" = mul i64 %"result_load", %"b_load"
  store i64 %"mul", i64* %"result"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"b_load.1" = load i64, i64* %"b"
  %"b_load.2" = load i64, i64* %"b"
  %"mul.1" = mul i64 %"b_load.1", %"b_load.2"
  store i64 %"mul.1", i64* %"b"
  %"e_load.2" = load i64, i64* %"e"
  %"ashr" = ashr i64 %"e_load.2", 1
  store i64 %"ashr", i64* %"e"
  br label %"while_cond"
}

define i64 @"is_prime"(i64 %".1")
{
is_prime_entry:
  %"n" = alloca i64
  store i64 %".1", i64* %"n"
  br label %"is_prime_body"
is_prime_body:
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"n_load", 2
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"n_load.1" = load i64, i64* %"n"
  %"icmp.1" = icmp slt i64 %"n_load.1", 4
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  ret i64 1
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"n_load.2" = load i64, i64* %"n"
  %"bitand" = and i64 %"n_load.2", 1
  %"icmp.2" = icmp eq i64 %"bitand", 0
  br i1 %"icmp.2", label %"if_then.2", label %"if_else.2"
if_then.2:
  ret i64 0
if_else.2:
  br label %"if_end.2"
if_end.2:
  %"i" = alloca i64
  store i64 3, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"i_load.1" = load i64, i64* %"i"
  %"mul" = mul i64 %"i_load", %"i_load.1"
  %"n_load.3" = load i64, i64* %"n"
  %"icmp.3" = icmp sle i64 %"mul", %"n_load.3"
  br i1 %"icmp.3", label %"while_body", label %"while_end"
while_body:
  %"n_load.4" = load i64, i64* %"n"
  %"i_load.2" = load i64, i64* %"i"
  %"mod" = srem i64 %"n_load.4", %"i_load.2"
  %"icmp.4" = icmp eq i64 %"mod", 0
  br i1 %"icmp.4", label %"if_then.3", label %"if_else.3"
while_end:
  ret i64 1
if_then.3:
  ret i64 0
if_else.3:
  br label %"if_end.3"
if_end.3:
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 2
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

define i64 @"random_int"(i64 %".1", i64 %".2")
{
random_int_entry:
  %"lo" = alloca i64
  store i64 %".1", i64* %"lo"
  %"hi" = alloca i64
  store i64 %".2", i64* %"hi"
  br label %"random_int_body"
random_int_body:
  %"hi_load" = load i64, i64* %"hi"
  %"lo_load" = load i64, i64* %"lo"
  %"sub" = sub i64 %"hi_load", %"lo_load"
  %"add" = add i64 %"sub", 1
  %"span" = alloca i64
  store i64 %"add", i64* %"span"
  %"span_load" = load i64, i64* %"span"
  %"icmp" = icmp sle i64 %"span_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"lo_load.1" = load i64, i64* %"lo"
  ret i64 %"lo_load.1"
if_else:
  br label %"if_end"
if_end:
  %"rand_call" = call i64 @"rand"()
  %"r" = alloca i64
  store i64 %"rand_call", i64* %"r"
  %"r_load" = load i64, i64* %"r"
  %"icmp.1" = icmp slt i64 %"r_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"lo_load.2" = load i64, i64* %"lo"
  ret i64 %"lo_load.2"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"lo_load.3" = load i64, i64* %"lo"
  %"r_load.1" = load i64, i64* %"r"
  %"span_load.1" = load i64, i64* %"span"
  %"mod" = srem i64 %"r_load.1", %"span_load.1"
  %"add.1" = add i64 %"lo_load.3", %"mod"
  ret i64 %"add.1"
}

declare i64 @"remove"(i8* %".1")

define i64 @"deletar_arquivo"(i8* %".1")
{
deletar_arquivo_entry:
  %"path" = alloca i8*
  store i8* %".1", i8** %"path"
  br label %"deletar_arquivo_body"
deletar_arquivo_body:
  %"path_load" = load i8*, i8** %"path"
  %"remove_call" = call i64 @"remove"(i8* %"path_load")
  ret i64 %"remove_call"
}

@"str_0" = constant [29 x i8] c"Testando a Standard Library:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [19 x i8] c"2 elevado a 10 \c3\a9:\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [3 x i8] c"%f\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [16 x i8] c"Raiz de 144 \c3\a9:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [3 x i8] c"%f\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [22 x i8] c"Criando um arquivo...\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c"\0a\00"
@"str_16" = constant [10 x i8] c"teste.txt\00"
@"str_17" = constant [20 x i8] c"Conteudo da stdlib!\00"
declare i8* @"fopen"(i8* %".1", i8* %".2")

declare i32 @"fputs"(i8* %".1", i8* %".2")

declare i32 @"fclose"(i8* %".1")

@"str_18" = constant [2 x i8] c"w\00"
@"str_19" = constant [23 x i8] c"Deletando o arquivo...\00"
@"str_20" = constant [3 x i8] c"%s\00"
@"str_21" = constant [2 x i8] c"\0a\00"
@"str_22" = constant [10 x i8] c"teste.txt\00"
@"str_23" = constant [30 x i8] c"C\c3\b3digo de retorno do delete:\00"
@"str_24" = constant [3 x i8] c"%s\00"
@"str_25" = constant [2 x i8] c" \00"
@"str_26" = constant [4 x i8] c"%ld\00"
@"str_27" = constant [2 x i8] c"\0a\00"