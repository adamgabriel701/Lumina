; ModuleID = "lumina_module"
target triple = "x86_64-pc-linux-gnu"
target datalayout = ""

declare i32 @"printf"(i8* %".1", ...)

declare i32 @"scanf"(i8* %".1", ...)

declare i32 @"sprintf"(i8* %".1", i8* %".2", ...)

declare i64 @"atoi"(i8* %".1")

declare i8* @"malloc"(i64 %".1")

declare void @"free"(i8* %".1")

declare i8* @"fopen"(i8* %".1", i8* %".2")

declare i8* @"fgets"(i8* %".1", i32 %".2", i8* %".3")

declare i32 @"fputs"(i8* %".1", i8* %".2")

declare void @"fclose"(i8* %".1")

declare double @"sqrt"(double %".1")

declare double @"pow"(double %".1", double %".2")

declare double @"sin"(double %".1")

declare double @"cos"(double %".1")

define double @"raiz_quadrada"(double %".1")
{
entry:
  %"n" = alloca double
  store double %".1", double* %"n"
  %"n_val" = load double, double* %"n"
  %"sqrt_call" = call double @"sqrt"(double %"n_val")
  ret double %"sqrt_call"
}

define double @"potencia"(double %".1", double %".2")
{
entry:
  %"base" = alloca double
  store double %".1", double* %"base"
  %"exp" = alloca double
  store double %".2", double* %"exp"
  %"base_val" = load double, double* %"base"
  %"exp_val" = load double, double* %"exp"
  %"pow_call" = call double @"pow"(double %"base_val", double %"exp_val")
  ret double %"pow_call"
}

declare i64 @"remove"(i8* %".1")

define i64 @"deletar_arquivo"(i8* %".1")
{
entry:
  %"path" = alloca i8*
  store i8* %".1", i8** %"path"
  %"path_val" = load i8*, i8** %"path"
  %"remove_call" = call i64 @"remove"(i8* %"path_val")
  ret i64 %"remove_call"
}

define i64 @"main"(i32 %".1", i8** %".2")
{
entry:
  %".4" = bitcast [29 x i8]* @"str_0" to i8*
  %".5" = bitcast [4 x i8]* @"str_1" to i8*
  %".6" = call i32 (i8*, ...) @"printf"(i8* %".5", i8* %".4")
  %".7" = bitcast [2 x i8]* @"str_2" to i8*
  %".8" = call i32 (i8*, ...) @"printf"(i8* %".7")
  %"base" = alloca double
  store double 0x4000000000000000, double* %"base"
  %"exp" = alloca double
  store double 0x4024000000000000, double* %"exp"
  %"base_val" = load double, double* %"base"
  %"exp_val" = load double, double* %"exp"
  %"potencia_call" = call double @"potencia"(double %"base_val", double %"exp_val")
  %"res" = alloca double
  store double %"potencia_call", double* %"res"
  %".12" = bitcast [19 x i8]* @"str_3" to i8*
  %".13" = bitcast [4 x i8]* @"str_4" to i8*
  %".14" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %".12")
  %"res_val" = load double, double* %"res"
  %".15" = bitcast [4 x i8]* @"str_5" to i8*
  %".16" = call i32 (i8*, ...) @"printf"(i8* %".15", double %"res_val")
  %".17" = bitcast [2 x i8]* @"str_6" to i8*
  %".18" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %"raiz_quadrada_call" = call double @"raiz_quadrada"(double 0x4062000000000000)
  %"raiz" = alloca double
  store double %"raiz_quadrada_call", double* %"raiz"
  %".20" = bitcast [16 x i8]* @"str_7" to i8*
  %".21" = bitcast [4 x i8]* @"str_8" to i8*
  %".22" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".20")
  %"raiz_val" = load double, double* %"raiz"
  %".23" = bitcast [4 x i8]* @"str_9" to i8*
  %".24" = call i32 (i8*, ...) @"printf"(i8* %".23", double %"raiz_val")
  %".25" = bitcast [2 x i8]* @"str_10" to i8*
  %".26" = call i32 (i8*, ...) @"printf"(i8* %".25")
  %".27" = bitcast [22 x i8]* @"str_11" to i8*
  %".28" = bitcast [4 x i8]* @"str_12" to i8*
  %".29" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %".30" = bitcast [2 x i8]* @"str_13" to i8*
  %".31" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %".32" = bitcast [10 x i8]* @"str_14" to i8*
  %".33" = bitcast [20 x i8]* @"str_15" to i8*
  %".34" = bitcast [2 x i8]* @"str_16" to i8*
  %"file_ptr_w" = call i8* @"fopen"(i8* %".32", i8* %".34")
  %".35" = call i32 @"fputs"(i8* %".33", i8* %"file_ptr_w")
  call void @"fclose"(i8* %"file_ptr_w")
  %".37" = bitcast [23 x i8]* @"str_17" to i8*
  %".38" = bitcast [4 x i8]* @"str_18" to i8*
  %".39" = call i32 (i8*, ...) @"printf"(i8* %".38", i8* %".37")
  %".40" = bitcast [2 x i8]* @"str_19" to i8*
  %".41" = call i32 (i8*, ...) @"printf"(i8* %".40")
  %".42" = bitcast [10 x i8]* @"str_20" to i8*
  %"deletar_arquivo_call" = call i64 @"deletar_arquivo"(i8* %".42")
  %"ret" = alloca i64
  store i64 %"deletar_arquivo_call", i64* %"ret"
  %".44" = bitcast [30 x i8]* @"str_21" to i8*
  %".45" = bitcast [4 x i8]* @"str_22" to i8*
  %".46" = call i32 (i8*, ...) @"printf"(i8* %".45", i8* %".44")
  %"ret_val" = load i64, i64* %"ret"
  %".47" = bitcast [4 x i8]* @"str_23" to i8*
  %".48" = call i32 (i8*, ...) @"printf"(i8* %".47", i64 %"ret_val")
  %".49" = bitcast [2 x i8]* @"str_24" to i8*
  %".50" = call i32 (i8*, ...) @"printf"(i8* %".49")
  ret i64 0
}

@"str_0" = constant [29 x i8] c"Testando a Standard Library:\00"
@"str_1" = constant [4 x i8] c"%s \00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [19 x i8] c"2 elevado a 10 \c3\a9:\00"
@"str_4" = constant [4 x i8] c"%s \00"
@"str_5" = constant [4 x i8] c"%f \00"
@"str_6" = constant [2 x i8] c"\0a\00"
@"str_7" = constant [16 x i8] c"Raiz de 144 \c3\a9:\00"
@"str_8" = constant [4 x i8] c"%s \00"
@"str_9" = constant [4 x i8] c"%f \00"
@"str_10" = constant [2 x i8] c"\0a\00"
@"str_11" = constant [22 x i8] c"Criando um arquivo...\00"
@"str_12" = constant [4 x i8] c"%s \00"
@"str_13" = constant [2 x i8] c"\0a\00"
@"str_14" = constant [10 x i8] c"teste.txt\00"
@"str_15" = constant [20 x i8] c"Conteudo da stdlib!\00"
@"str_16" = constant [2 x i8] c"w\00"
@"str_17" = constant [23 x i8] c"Deletando o arquivo...\00"
@"str_18" = constant [4 x i8] c"%s \00"
@"str_19" = constant [2 x i8] c"\0a\00"
@"str_20" = constant [10 x i8] c"teste.txt\00"
@"str_21" = constant [30 x i8] c"C\c3\b3digo de retorno do delete:\00"
@"str_22" = constant [4 x i8] c"%s \00"
@"str_23" = constant [4 x i8] c"%d \00"
@"str_24" = constant [2 x i8] c"\0a\00"