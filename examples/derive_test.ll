; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Ponto" = type {i64, i64}
%"Pessoa" = type {i64, i64}
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
  %"p1" = alloca %"Ponto"*
  %"p1_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"p1_storage" = bitcast i8* %"p1_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"p1_storage"
  store %"Ponto"* %"p1_storage", %"Ponto"** %"p1"
  %"p1_load" = load %"Ponto"*, %"Ponto"** %"p1"
  %"x_ptr" = getelementptr %"Ponto", %"Ponto"* %"p1_load", i32 0, i32 0
  store i64 10, i64* %"x_ptr"
  %"p1_load.1" = load %"Ponto"*, %"Ponto"** %"p1"
  %"y_ptr" = getelementptr %"Ponto", %"Ponto"* %"p1_load.1", i32 0, i32 1
  store i64 20, i64* %"y_ptr"
  %"p2" = alloca %"Ponto"*
  %"p2_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"p2_storage" = bitcast i8* %"p2_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"p2_storage"
  store %"Ponto"* %"p2_storage", %"Ponto"** %"p2"
  %"p2_load" = load %"Ponto"*, %"Ponto"** %"p2"
  %"x_ptr.1" = getelementptr %"Ponto", %"Ponto"* %"p2_load", i32 0, i32 0
  store i64 10, i64* %"x_ptr.1"
  %"p2_load.1" = load %"Ponto"*, %"Ponto"** %"p2"
  %"y_ptr.1" = getelementptr %"Ponto", %"Ponto"* %"p2_load.1", i32 0, i32 1
  store i64 20, i64* %"y_ptr.1"
  %"p3" = alloca %"Ponto"*
  %"p3_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"p3_storage" = bitcast i8* %"p3_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"p3_storage"
  store %"Ponto"* %"p3_storage", %"Ponto"** %"p3"
  %"p3_load" = load %"Ponto"*, %"Ponto"** %"p3"
  %"x_ptr.2" = getelementptr %"Ponto", %"Ponto"* %"p3_load", i32 0, i32 0
  store i64 10, i64* %"x_ptr.2"
  %"p3_load.1" = load %"Ponto"*, %"Ponto"** %"p3"
  %"y_ptr.2" = getelementptr %"Ponto", %"Ponto"* %"p3_load.1", i32 0, i32 1
  store i64 99, i64* %"y_ptr.2"
  %".19" = bitcast [11 x i8]* @"str_0" to i8*
  %".20" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %".21" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [10 x i8]* @"str_3" to i8*
  %".23" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %"p1_load.2" = load %"Ponto"*, %"Ponto"** %"p1"
  %"p2_load.2" = load %"Ponto"*, %"Ponto"** %"p2"
  %"op_Ponto___eq__" = call i1 @"Ponto___eq__"(%"Ponto"* %"p1_load.2", %"Ponto"* %"p2_load.2")
  %".24" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [5 x i8]* @"str_6" to i8*
  %".26" = bitcast [6 x i8]* @"str_7" to i8*
  %"print_bool" = select  i1 %"op_Ponto___eq__", i8* %".25", i8* %".26"
  %".27" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".27", i8* %"print_bool")
  %".28" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".28")
  %".29" = bitcast [10 x i8]* @"str_10" to i8*
  %".30" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %".29")
  %"p1_load.3" = load %"Ponto"*, %"Ponto"** %"p1"
  %"p3_load.2" = load %"Ponto"*, %"Ponto"** %"p3"
  %"op_Ponto___eq__.1" = call i1 @"Ponto___eq__"(%"Ponto"* %"p1_load.3", %"Ponto"* %"p3_load.2")
  %".31" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [5 x i8]* @"str_13" to i8*
  %".33" = bitcast [6 x i8]* @"str_14" to i8*
  %"print_bool.1" = select  i1 %"op_Ponto___eq__.1", i8* %".32", i8* %".33"
  %".34" = bitcast [3 x i8]* @"str_15" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".34", i8* %"print_bool.1")
  %".35" = bitcast [2 x i8]* @"str_16" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".35")
  %".36" = bitcast [14 x i8]* @"str_17" to i8*
  %".37" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".37", i8* %".36")
  %".38" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".38")
  %"p1_load.4" = load %"Ponto"*, %"Ponto"** %"p1"
  %"Ponto___debug___call" = call i8* @"Ponto___debug__"(%"Ponto"* %"p1_load.4")
  %".39" = bitcast [3 x i8]* @"str_20" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".39", i8* %"Ponto___debug___call")
  %".40" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".40")
  %".41" = bitcast [18 x i8]* @"str_22" to i8*
  %".42" = bitcast [3 x i8]* @"str_23" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".42", i8* %".41")
  %".43" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".43")
  %"a" = alloca %"Pessoa"*
  %"a_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"a_storage" = bitcast i8* %"a_storage_raw" to %"Pessoa"*
  store %"Pessoa" {i64 0, i64 0}, %"Pessoa"* %"a_storage"
  store %"Pessoa"* %"a_storage", %"Pessoa"** %"a"
  %"a_load" = load %"Pessoa"*, %"Pessoa"** %"a"
  %"idade_ptr" = getelementptr %"Pessoa", %"Pessoa"* %"a_load", i32 0, i32 0
  store i64 30, i64* %"idade_ptr"
  %"a_load.1" = load %"Pessoa"*, %"Pessoa"** %"a"
  %"ativo_ptr" = getelementptr %"Pessoa", %"Pessoa"* %"a_load.1", i32 0, i32 1
  store i64 1, i64* %"ativo_ptr"
  %"b" = alloca %"Pessoa"*
  %"b_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"b_storage" = bitcast i8* %"b_storage_raw" to %"Pessoa"*
  store %"Pessoa" {i64 0, i64 0}, %"Pessoa"* %"b_storage"
  store %"Pessoa"* %"b_storage", %"Pessoa"** %"b"
  %"b_load" = load %"Pessoa"*, %"Pessoa"** %"b"
  %"idade_ptr.1" = getelementptr %"Pessoa", %"Pessoa"* %"b_load", i32 0, i32 0
  store i64 30, i64* %"idade_ptr.1"
  %"b_load.1" = load %"Pessoa"*, %"Pessoa"** %"b"
  %"ativo_ptr.1" = getelementptr %"Pessoa", %"Pessoa"* %"b_load.1", i32 0, i32 1
  store i64 1, i64* %"ativo_ptr.1"
  %".52" = bitcast [8 x i8]* @"str_25" to i8*
  %".53" = bitcast [3 x i8]* @"str_26" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".53", i8* %".52")
  %"a_load.2" = load %"Pessoa"*, %"Pessoa"** %"a"
  %"b_load.2" = load %"Pessoa"*, %"Pessoa"** %"b"
  %"op_Pessoa___eq__" = call i1 @"Pessoa___eq__"(%"Pessoa"* %"a_load.2", %"Pessoa"* %"b_load.2")
  %".54" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".54")
  %".55" = bitcast [5 x i8]* @"str_28" to i8*
  %".56" = bitcast [6 x i8]* @"str_29" to i8*
  %"print_bool.2" = select  i1 %"op_Pessoa___eq__", i8* %".55", i8* %".56"
  %".57" = bitcast [3 x i8]* @"str_30" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".57", i8* %"print_bool.2")
  %".58" = bitcast [2 x i8]* @"str_31" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".58")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define i1 @"Ponto___eq__"(%"Ponto"* %".1", %"Ponto"* %".2")
{
Ponto___eq___entry:
  %"a" = alloca %"Ponto"*
  store %"Ponto"* %".1", %"Ponto"** %"a"
  %"b" = alloca %"Ponto"*
  store %"Ponto"* %".2", %"Ponto"** %"b"
  br label %"Ponto___eq___body"
Ponto___eq___body:
  %"a_load" = load %"Ponto"*, %"Ponto"** %"a"
  %".7" = getelementptr %"Ponto", %"Ponto"* %"a_load", i32 0, i32 0
  %"x_load" = load i64, i64* %".7"
  %"b_load" = load %"Ponto"*, %"Ponto"** %"b"
  %".8" = getelementptr %"Ponto", %"Ponto"* %"b_load", i32 0, i32 0
  %"x_load.1" = load i64, i64* %".8"
  %"icmp" = icmp eq i64 %"x_load", %"x_load.1"
  br i1 %"icmp", label %"and_rhs", label %"and_end"
and_rhs:
  %"a_load.1" = load %"Ponto"*, %"Ponto"** %"a"
  %".10" = getelementptr %"Ponto", %"Ponto"* %"a_load.1", i32 0, i32 1
  %"y_load" = load i64, i64* %".10"
  %"b_load.1" = load %"Ponto"*, %"Ponto"** %"b"
  %".11" = getelementptr %"Ponto", %"Ponto"* %"b_load.1", i32 0, i32 1
  %"y_load.1" = load i64, i64* %".11"
  %"icmp.1" = icmp eq i64 %"y_load", %"y_load.1"
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"Ponto___eq___body"], [%"icmp.1", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  ret i1 1
if_else:
  br label %"if_end"
if_end:
  ret i1 0
}

define i8* @"Ponto___debug__"(%"Ponto"* %".1")
{
Ponto___debug___entry:
  %"p" = alloca %"Ponto"*
  store %"Ponto"* %".1", %"Ponto"** %"p"
  br label %"Ponto___debug___body"
Ponto___debug___body:
  %".5" = bitcast [9 x i8]* @"str_32" to i8*
  %".6" = bitcast [4 x i8]* @"str_33" to i8*
  %"sconcat_len1" = call i64 @"strlen"(i8* %".5")
  %"sconcat_len2" = call i64 @"strlen"(i8* %".6")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".5")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %".6")
  %"p_load" = load %"Ponto"*, %"Ponto"** %"p"
  %".7" = getelementptr %"Ponto", %"Ponto"* %"p_load", i32 0, i32 0
  %"x_load" = load i64, i64* %".7"
  %".8" = bitcast [4 x i8]* @"str_34" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".8", i64 %"x_load")
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %"num_to_str_ptr")
  %".9" = bitcast [3 x i8]* @"str_35" to i8*
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %".9")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %".9")
  %".10" = bitcast [4 x i8]* @"str_36" to i8*
  %"sconcat_len1.3" = call i64 @"strlen"(i8* %"sconcat_buf.2")
  %"sconcat_len2.3" = call i64 @"strlen"(i8* %".10")
  %"sconcat_sum.3" = add i64 %"sconcat_len1.3", %"sconcat_len2.3"
  %"sconcat_total.3" = add i64 %"sconcat_sum.3", 1
  %"sconcat_buf.3" = call i8* @"GC_malloc"(i64 %"sconcat_total.3")
  %"sconcat_cpy.3" = call i8* @"strcpy"(i8* %"sconcat_buf.3", i8* %"sconcat_buf.2")
  %"sconcat_cat.3" = call i8* @"strcat"(i8* %"sconcat_buf.3", i8* %".10")
  %"p_load.1" = load %"Ponto"*, %"Ponto"** %"p"
  %".11" = getelementptr %"Ponto", %"Ponto"* %"p_load.1", i32 0, i32 1
  %"y_load" = load i64, i64* %".11"
  %".12" = bitcast [4 x i8]* @"str_37" to i8*
  %"num_to_str.1" = alloca [64 x i8]
  %"num_to_str_ptr.1" = bitcast [64 x i8]* %"num_to_str.1" to i8*
  %"num_to_str_call.1" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr.1", i64 64, i8* %".12", i64 %"y_load")
  %"sconcat_len1.4" = call i64 @"strlen"(i8* %"sconcat_buf.3")
  %"sconcat_len2.4" = call i64 @"strlen"(i8* %"num_to_str_ptr.1")
  %"sconcat_sum.4" = add i64 %"sconcat_len1.4", %"sconcat_len2.4"
  %"sconcat_total.4" = add i64 %"sconcat_sum.4", 1
  %"sconcat_buf.4" = call i8* @"GC_malloc"(i64 %"sconcat_total.4")
  %"sconcat_cpy.4" = call i8* @"strcpy"(i8* %"sconcat_buf.4", i8* %"sconcat_buf.3")
  %"sconcat_cat.4" = call i8* @"strcat"(i8* %"sconcat_buf.4", i8* %"num_to_str_ptr.1")
  %".13" = bitcast [3 x i8]* @"str_38" to i8*
  %"sconcat_len1.5" = call i64 @"strlen"(i8* %"sconcat_buf.4")
  %"sconcat_len2.5" = call i64 @"strlen"(i8* %".13")
  %"sconcat_sum.5" = add i64 %"sconcat_len1.5", %"sconcat_len2.5"
  %"sconcat_total.5" = add i64 %"sconcat_sum.5", 1
  %"sconcat_buf.5" = call i8* @"GC_malloc"(i64 %"sconcat_total.5")
  %"sconcat_cpy.5" = call i8* @"strcpy"(i8* %"sconcat_buf.5", i8* %"sconcat_buf.4")
  %"sconcat_cat.5" = call i8* @"strcat"(i8* %"sconcat_buf.5", i8* %".13")
  ret i8* %"sconcat_buf.5"
}

define i1 @"Pessoa___eq__"(%"Pessoa"* %".1", %"Pessoa"* %".2")
{
Pessoa___eq___entry:
  %"a" = alloca %"Pessoa"*
  store %"Pessoa"* %".1", %"Pessoa"** %"a"
  %"b" = alloca %"Pessoa"*
  store %"Pessoa"* %".2", %"Pessoa"** %"b"
  br label %"Pessoa___eq___body"
Pessoa___eq___body:
  %"a_load" = load %"Pessoa"*, %"Pessoa"** %"a"
  %".7" = getelementptr %"Pessoa", %"Pessoa"* %"a_load", i32 0, i32 0
  %"idade_load" = load i64, i64* %".7"
  %"b_load" = load %"Pessoa"*, %"Pessoa"** %"b"
  %".8" = getelementptr %"Pessoa", %"Pessoa"* %"b_load", i32 0, i32 0
  %"idade_load.1" = load i64, i64* %".8"
  %"icmp" = icmp eq i64 %"idade_load", %"idade_load.1"
  br i1 %"icmp", label %"and_rhs", label %"and_end"
and_rhs:
  %"a_load.1" = load %"Pessoa"*, %"Pessoa"** %"a"
  %".10" = getelementptr %"Pessoa", %"Pessoa"* %"a_load.1", i32 0, i32 1
  %"ativo_load" = load i64, i64* %".10"
  %"b_load.1" = load %"Pessoa"*, %"Pessoa"** %"b"
  %".11" = getelementptr %"Pessoa", %"Pessoa"* %"b_load.1", i32 0, i32 1
  %"ativo_load.1" = load i64, i64* %".11"
  %"icmp.1" = icmp eq i64 %"ativo_load", %"ativo_load.1"
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"Pessoa___eq___body"], [%"icmp.1", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  ret i1 1
if_else:
  br label %"if_end"
if_end:
  ret i1 0
}

@"str_0" = constant [11 x i8] c"=== Eq ===\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [10 x i8] c"p1 == p2?\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [5 x i8] c"true\00"
@"str_7" = constant [6 x i8] c"false\00"
@"str_8" = constant [3 x i8] c"%s\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [10 x i8] c"p1 == p3?\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c" \00"
@"str_13" = constant [5 x i8] c"true\00"
@"str_14" = constant [6 x i8] c"false\00"
@"str_15" = constant [3 x i8] c"%s\00"
@"str_16" = constant [2 x i8] c"\0a\00"
@"str_17" = constant [14 x i8] c"=== Debug ===\00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c"\0a\00"
@"str_20" = constant [3 x i8] c"%s\00"
@"str_21" = constant [2 x i8] c"\0a\00"
@"str_22" = constant [18 x i8] c"=== Pessoa Eq ===\00"
@"str_23" = constant [3 x i8] c"%s\00"
@"str_24" = constant [2 x i8] c"\0a\00"
@"str_25" = constant [8 x i8] c"a == b?\00"
@"str_26" = constant [3 x i8] c"%s\00"
@"str_27" = constant [2 x i8] c" \00"
@"str_28" = constant [5 x i8] c"true\00"
@"str_29" = constant [6 x i8] c"false\00"
@"str_30" = constant [3 x i8] c"%s\00"
@"str_31" = constant [2 x i8] c"\0a\00"
@"str_32" = constant [9 x i8] c"Ponto { \00"
@"str_33" = constant [4 x i8] c"x: \00"
@"str_34" = constant [4 x i8] c"%ld\00"
@"str_35" = constant [3 x i8] c", \00"
@"str_36" = constant [4 x i8] c"y: \00"
@"str_37" = constant [4 x i8] c"%ld\00"
@"str_38" = constant [3 x i8] c" }\00"