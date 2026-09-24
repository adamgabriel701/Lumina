; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Ponto" = type {i64, i64}
%"Pessoa" = type {i64, double, i1}
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
  %".7" = bitcast [16 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %"new_Ponto_call" = call %"Ponto"* @"new_Ponto"()
  %"p1" = alloca %"Ponto"*
  store %"Ponto"* %"new_Ponto_call", %"Ponto"** %"p1"
  %".11" = bitcast [7 x i8]* @"str_3" to i8*
  %".12" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".12", i8* %".11")
  %"p1_load" = load %"Ponto"*, %"Ponto"** %"p1"
  %".13" = getelementptr %"Ponto", %"Ponto"* %"p1_load", i32 0, i32 0
  %"x_load" = load i64, i64* %".13"
  %".14" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".15", i64 %"x_load")
  %".16" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [7 x i8]* @"str_8" to i8*
  %".18" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %".17")
  %"p1_load.1" = load %"Ponto"*, %"Ponto"** %"p1"
  %".19" = getelementptr %"Ponto", %"Ponto"* %"p1_load.1", i32 0, i32 1
  %"y_load" = load i64, i64* %".19"
  %".20" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %".21" = bitcast [4 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".21", i64 %"y_load")
  %".22" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %"new_Pessoa_call" = call %"Pessoa"* @"new_Pessoa"()
  %"pessoa" = alloca %"Pessoa"*
  store %"Pessoa"* %"new_Pessoa_call", %"Pessoa"** %"pessoa"
  %".24" = bitcast [15 x i8]* @"str_13" to i8*
  %".25" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %".24")
  %"pessoa_load" = load %"Pessoa"*, %"Pessoa"** %"pessoa"
  %".26" = getelementptr %"Pessoa", %"Pessoa"* %"pessoa_load", i32 0, i32 0
  %"idade_load" = load i64, i64* %".26"
  %".27" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".27")
  %".28" = bitcast [4 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".28", i64 %"idade_load")
  %".29" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [15 x i8]* @"str_18" to i8*
  %".31" = bitcast [3 x i8]* @"str_19" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".31", i8* %".30")
  %"pessoa_load.1" = load %"Pessoa"*, %"Pessoa"** %"pessoa"
  %".32" = getelementptr %"Pessoa", %"Pessoa"* %"pessoa_load.1", i32 0, i32 2
  %"ativo_load" = load i1, i1* %".32"
  %".33" = bitcast [2 x i8]* @"str_20" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".33")
  %".34" = bitcast [5 x i8]* @"str_21" to i8*
  %".35" = bitcast [6 x i8]* @"str_22" to i8*
  %"print_bool" = select  i1 %"ativo_load", i8* %".34", i8* %".35"
  %".36" = bitcast [3 x i8]* @"str_23" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".36", i8* %"print_bool")
  %".37" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".37")
  %".38" = bitcast [14 x i8]* @"str_25" to i8*
  %".39" = bitcast [3 x i8]* @"str_26" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".39", i8* %".38")
  %".40" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".40")
  %"original" = alloca %"Ponto"*
  %"original_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"original_storage" = bitcast i8* %"original_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"original_storage"
  store %"Ponto"* %"original_storage", %"Ponto"** %"original"
  %"original_load" = load %"Ponto"*, %"Ponto"** %"original"
  %"x_ptr" = getelementptr %"Ponto", %"Ponto"* %"original_load", i32 0, i32 0
  store i64 10, i64* %"x_ptr"
  %"original_load.1" = load %"Ponto"*, %"Ponto"** %"original"
  %"y_ptr" = getelementptr %"Ponto", %"Ponto"* %"original_load.1", i32 0, i32 1
  store i64 20, i64* %"y_ptr"
  %"original_load.2" = load %"Ponto"*, %"Ponto"** %"original"
  %"Ponto_clone_call" = call %"Ponto"* @"Ponto_clone"(%"Ponto"* %"original_load.2")
  %"copia" = alloca %"Ponto"*
  store %"Ponto"* %"Ponto_clone_call", %"Ponto"** %"copia"
  %".46" = bitcast [10 x i8]* @"str_28" to i8*
  %".47" = bitcast [3 x i8]* @"str_29" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".47", i8* %".46")
  %"copia_load" = load %"Ponto"*, %"Ponto"** %"copia"
  %".48" = getelementptr %"Ponto", %"Ponto"* %"copia_load", i32 0, i32 0
  %"x_load.1" = load i64, i64* %".48"
  %".49" = bitcast [2 x i8]* @"str_30" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".49")
  %".50" = bitcast [4 x i8]* @"str_31" to i8*
  %"print_call.11" = call i32 (i8*, ...) @"printf"(i8* %".50", i64 %"x_load.1")
  %".51" = bitcast [2 x i8]* @"str_32" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".51")
  %".52" = bitcast [10 x i8]* @"str_33" to i8*
  %".53" = bitcast [3 x i8]* @"str_34" to i8*
  %"print_call.12" = call i32 (i8*, ...) @"printf"(i8* %".53", i8* %".52")
  %"copia_load.1" = load %"Ponto"*, %"Ponto"** %"copia"
  %".54" = getelementptr %"Ponto", %"Ponto"* %"copia_load.1", i32 0, i32 1
  %"y_load.1" = load i64, i64* %".54"
  %".55" = bitcast [2 x i8]* @"str_35" to i8*
  %"print_sep.5" = call i32 (i8*, ...) @"printf"(i8* %".55")
  %".56" = bitcast [4 x i8]* @"str_36" to i8*
  %"print_call.13" = call i32 (i8*, ...) @"printf"(i8* %".56", i64 %"y_load.1")
  %".57" = bitcast [2 x i8]* @"str_37" to i8*
  %"print_nl.7" = call i32 (i8*, ...) @"printf"(i8* %".57")
  %".58" = bitcast [11 x i8]* @"str_38" to i8*
  %".59" = bitcast [3 x i8]* @"str_39" to i8*
  %"print_call.14" = call i32 (i8*, ...) @"printf"(i8* %".59", i8* %".58")
  %".60" = bitcast [2 x i8]* @"str_40" to i8*
  %"print_nl.8" = call i32 (i8*, ...) @"printf"(i8* %".60")
  %"new_Ponto_call.1" = call %"Ponto"* @"new_Ponto"()
  %"a" = alloca %"Ponto"*
  store %"Ponto"* %"new_Ponto_call.1", %"Ponto"** %"a"
  %"new_Ponto_call.2" = call %"Ponto"* @"new_Ponto"()
  %"b" = alloca %"Ponto"*
  store %"Ponto"* %"new_Ponto_call.2", %"Ponto"** %"b"
  %".63" = bitcast [8 x i8]* @"str_41" to i8*
  %".64" = bitcast [3 x i8]* @"str_42" to i8*
  %"print_call.15" = call i32 (i8*, ...) @"printf"(i8* %".64", i8* %".63")
  %"a_load" = load %"Ponto"*, %"Ponto"** %"a"
  %"b_load" = load %"Ponto"*, %"Ponto"** %"b"
  %"op_Ponto___eq__" = call i1 @"Ponto___eq__"(%"Ponto"* %"a_load", %"Ponto"* %"b_load")
  %".65" = bitcast [2 x i8]* @"str_43" to i8*
  %"print_sep.6" = call i32 (i8*, ...) @"printf"(i8* %".65")
  %".66" = bitcast [5 x i8]* @"str_44" to i8*
  %".67" = bitcast [6 x i8]* @"str_45" to i8*
  %"print_bool.1" = select  i1 %"op_Ponto___eq__", i8* %".66", i8* %".67"
  %".68" = bitcast [3 x i8]* @"str_46" to i8*
  %"print_call.16" = call i32 (i8*, ...) @"printf"(i8* %".68", i8* %"print_bool.1")
  %".69" = bitcast [2 x i8]* @"str_47" to i8*
  %"print_nl.9" = call i32 (i8*, ...) @"printf"(i8* %".69")
  %"c" = alloca %"Ponto"*
  %"c_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"c_storage" = bitcast i8* %"c_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"c_storage"
  store %"Ponto"* %"c_storage", %"Ponto"** %"c"
  %"c_load" = load %"Ponto"*, %"Ponto"** %"c"
  %"x_ptr.1" = getelementptr %"Ponto", %"Ponto"* %"c_load", i32 0, i32 0
  store i64 5, i64* %"x_ptr.1"
  %"c_load.1" = load %"Ponto"*, %"Ponto"** %"c"
  %"y_ptr.1" = getelementptr %"Ponto", %"Ponto"* %"c_load.1", i32 0, i32 1
  store i64 5, i64* %"y_ptr.1"
  %".74" = bitcast [8 x i8]* @"str_48" to i8*
  %".75" = bitcast [3 x i8]* @"str_49" to i8*
  %"print_call.17" = call i32 (i8*, ...) @"printf"(i8* %".75", i8* %".74")
  %"a_load.1" = load %"Ponto"*, %"Ponto"** %"a"
  %"c_load.2" = load %"Ponto"*, %"Ponto"** %"c"
  %"op_Ponto___eq__.1" = call i1 @"Ponto___eq__"(%"Ponto"* %"a_load.1", %"Ponto"* %"c_load.2")
  %".76" = bitcast [2 x i8]* @"str_50" to i8*
  %"print_sep.7" = call i32 (i8*, ...) @"printf"(i8* %".76")
  %".77" = bitcast [5 x i8]* @"str_51" to i8*
  %".78" = bitcast [6 x i8]* @"str_52" to i8*
  %"print_bool.2" = select  i1 %"op_Ponto___eq__.1", i8* %".77", i8* %".78"
  %".79" = bitcast [3 x i8]* @"str_53" to i8*
  %"print_call.18" = call i32 (i8*, ...) @"printf"(i8* %".79", i8* %"print_bool.2")
  %".80" = bitcast [2 x i8]* @"str_54" to i8*
  %"print_nl.10" = call i32 (i8*, ...) @"printf"(i8* %".80")
  %".81" = bitcast [14 x i8]* @"str_55" to i8*
  %".82" = bitcast [3 x i8]* @"str_56" to i8*
  %"print_call.19" = call i32 (i8*, ...) @"printf"(i8* %".82", i8* %".81")
  %".83" = bitcast [2 x i8]* @"str_57" to i8*
  %"print_nl.11" = call i32 (i8*, ...) @"printf"(i8* %".83")
  %"d" = alloca %"Ponto"*
  %"d_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"d_storage" = bitcast i8* %"d_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"d_storage"
  store %"Ponto"* %"d_storage", %"Ponto"** %"d"
  %"d_load" = load %"Ponto"*, %"Ponto"** %"d"
  %"x_ptr.2" = getelementptr %"Ponto", %"Ponto"* %"d_load", i32 0, i32 0
  store i64 1, i64* %"x_ptr.2"
  %"d_load.1" = load %"Ponto"*, %"Ponto"** %"d"
  %"y_ptr.2" = getelementptr %"Ponto", %"Ponto"* %"d_load.1", i32 0, i32 1
  store i64 2, i64* %"y_ptr.2"
  %"d_load.2" = load %"Ponto"*, %"Ponto"** %"d"
  %"Ponto___debug___call" = call i8* @"Ponto___debug__"(%"Ponto"* %"d_load.2")
  %".88" = bitcast [3 x i8]* @"str_58" to i8*
  %"print_call.20" = call i32 (i8*, ...) @"printf"(i8* %".88", i8* %"Ponto___debug___call")
  %".89" = bitcast [2 x i8]* @"str_59" to i8*
  %"print_nl.12" = call i32 (i8*, ...) @"printf"(i8* %".89")
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
  %".5" = bitcast [9 x i8]* @"str_60" to i8*
  %".6" = bitcast [4 x i8]* @"str_61" to i8*
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
  %".8" = bitcast [4 x i8]* @"str_62" to i8*
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
  %".9" = bitcast [3 x i8]* @"str_63" to i8*
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %".9")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %".9")
  %".10" = bitcast [4 x i8]* @"str_64" to i8*
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
  %".12" = bitcast [4 x i8]* @"str_65" to i8*
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
  %".13" = bitcast [3 x i8]* @"str_66" to i8*
  %"sconcat_len1.5" = call i64 @"strlen"(i8* %"sconcat_buf.4")
  %"sconcat_len2.5" = call i64 @"strlen"(i8* %".13")
  %"sconcat_sum.5" = add i64 %"sconcat_len1.5", %"sconcat_len2.5"
  %"sconcat_total.5" = add i64 %"sconcat_sum.5", 1
  %"sconcat_buf.5" = call i8* @"GC_malloc"(i64 %"sconcat_total.5")
  %"sconcat_cpy.5" = call i8* @"strcpy"(i8* %"sconcat_buf.5", i8* %"sconcat_buf.4")
  %"sconcat_cat.5" = call i8* @"strcat"(i8* %"sconcat_buf.5", i8* %".13")
  ret i8* %"sconcat_buf.5"
}

define %"Ponto"* @"Ponto_clone"(%"Ponto"* %".1")
{
Ponto_clone_entry:
  %"self" = alloca %"Ponto"*
  store %"Ponto"* %".1", %"Ponto"** %"self"
  br label %"Ponto_clone_body"
Ponto_clone_body:
  %"result" = alloca %"Ponto"*
  %"result_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"result_storage" = bitcast i8* %"result_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"result_storage"
  store %"Ponto"* %"result_storage", %"Ponto"** %"result"
  %"self_load" = load %"Ponto"*, %"Ponto"** %"self"
  %".7" = getelementptr %"Ponto", %"Ponto"* %"self_load", i32 0, i32 0
  %"x_load" = load i64, i64* %".7"
  %"result_load" = load %"Ponto"*, %"Ponto"** %"result"
  %"x_ptr" = getelementptr %"Ponto", %"Ponto"* %"result_load", i32 0, i32 0
  store i64 %"x_load", i64* %"x_ptr"
  %"self_load.1" = load %"Ponto"*, %"Ponto"** %"self"
  %".9" = getelementptr %"Ponto", %"Ponto"* %"self_load.1", i32 0, i32 1
  %"y_load" = load i64, i64* %".9"
  %"result_load.1" = load %"Ponto"*, %"Ponto"** %"result"
  %"y_ptr" = getelementptr %"Ponto", %"Ponto"* %"result_load.1", i32 0, i32 1
  store i64 %"y_load", i64* %"y_ptr"
  %"result_load.2" = load %"Ponto"*, %"Ponto"** %"result"
  ret %"Ponto"* %"result_load.2"
}

define %"Ponto"* @"new_Ponto"()
{
new_Ponto_entry:
  br label %"new_Ponto_body"
new_Ponto_body:
  %"result" = alloca %"Ponto"*
  %"result_storage_raw" = call i8* @"GC_malloc"(i64 16)
  %"result_storage" = bitcast i8* %"result_storage_raw" to %"Ponto"*
  store %"Ponto" {i64 0, i64 0}, %"Ponto"* %"result_storage"
  store %"Ponto"* %"result_storage", %"Ponto"** %"result"
  %"result_load" = load %"Ponto"*, %"Ponto"** %"result"
  %"x_ptr" = getelementptr %"Ponto", %"Ponto"* %"result_load", i32 0, i32 0
  store i64 0, i64* %"x_ptr"
  %"result_load.1" = load %"Ponto"*, %"Ponto"** %"result"
  %"y_ptr" = getelementptr %"Ponto", %"Ponto"* %"result_load.1", i32 0, i32 1
  store i64 0, i64* %"y_ptr"
  %"result_load.2" = load %"Ponto"*, %"Ponto"** %"result"
  ret %"Ponto"* %"result_load.2"
}

define %"Pessoa"* @"new_Pessoa"()
{
new_Pessoa_entry:
  br label %"new_Pessoa_body"
new_Pessoa_body:
  %"result" = alloca %"Pessoa"*
  %"result_storage_raw" = call i8* @"GC_malloc"(i64 24)
  %"result_storage" = bitcast i8* %"result_storage_raw" to %"Pessoa"*
  store %"Pessoa" {i64 0, double              0x0, i1 0}, %"Pessoa"* %"result_storage"
  store %"Pessoa"* %"result_storage", %"Pessoa"** %"result"
  %"result_load" = load %"Pessoa"*, %"Pessoa"** %"result"
  %"idade_ptr" = getelementptr %"Pessoa", %"Pessoa"* %"result_load", i32 0, i32 0
  store i64 0, i64* %"idade_ptr"
  %"result_load.1" = load %"Pessoa"*, %"Pessoa"** %"result"
  %"altura_ptr" = getelementptr %"Pessoa", %"Pessoa"* %"result_load.1", i32 0, i32 1
  store double              0x0, double* %"altura_ptr"
  %"result_load.2" = load %"Pessoa"*, %"Pessoa"** %"result"
  %"ativo_ptr" = getelementptr %"Pessoa", %"Pessoa"* %"result_load.2", i32 0, i32 2
  store i1 0, i1* %"ativo_ptr"
  %"result_load.3" = load %"Pessoa"*, %"Pessoa"** %"result"
  ret %"Pessoa"* %"result_load.3"
}

@"str_0" = constant [16 x i8] c"=== Default ===\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [7 x i8] c"p1.x =\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c"\0a\00"
@"str_8" = constant [7 x i8] c"p1.y =\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [4 x i8] c"%ld\00"
@"str_12" = constant [2 x i8] c"\0a\00"
@"str_13" = constant [15 x i8] c"pessoa.idade =\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [4 x i8] c"%ld\00"
@"str_17" = constant [2 x i8] c"\0a\00"
@"str_18" = constant [15 x i8] c"pessoa.ativo =\00"
@"str_19" = constant [3 x i8] c"%s\00"
@"str_20" = constant [2 x i8] c" \00"
@"str_21" = constant [5 x i8] c"true\00"
@"str_22" = constant [6 x i8] c"false\00"
@"str_23" = constant [3 x i8] c"%s\00"
@"str_24" = constant [2 x i8] c"\0a\00"
@"str_25" = constant [14 x i8] c"=== Clone ===\00"
@"str_26" = constant [3 x i8] c"%s\00"
@"str_27" = constant [2 x i8] c"\0a\00"
@"str_28" = constant [10 x i8] c"copia.x =\00"
@"str_29" = constant [3 x i8] c"%s\00"
@"str_30" = constant [2 x i8] c" \00"
@"str_31" = constant [4 x i8] c"%ld\00"
@"str_32" = constant [2 x i8] c"\0a\00"
@"str_33" = constant [10 x i8] c"copia.y =\00"
@"str_34" = constant [3 x i8] c"%s\00"
@"str_35" = constant [2 x i8] c" \00"
@"str_36" = constant [4 x i8] c"%ld\00"
@"str_37" = constant [2 x i8] c"\0a\00"
@"str_38" = constant [11 x i8] c"=== Eq ===\00"
@"str_39" = constant [3 x i8] c"%s\00"
@"str_40" = constant [2 x i8] c"\0a\00"
@"str_41" = constant [8 x i8] c"a == b?\00"
@"str_42" = constant [3 x i8] c"%s\00"
@"str_43" = constant [2 x i8] c" \00"
@"str_44" = constant [5 x i8] c"true\00"
@"str_45" = constant [6 x i8] c"false\00"
@"str_46" = constant [3 x i8] c"%s\00"
@"str_47" = constant [2 x i8] c"\0a\00"
@"str_48" = constant [8 x i8] c"a == c?\00"
@"str_49" = constant [3 x i8] c"%s\00"
@"str_50" = constant [2 x i8] c" \00"
@"str_51" = constant [5 x i8] c"true\00"
@"str_52" = constant [6 x i8] c"false\00"
@"str_53" = constant [3 x i8] c"%s\00"
@"str_54" = constant [2 x i8] c"\0a\00"
@"str_55" = constant [14 x i8] c"=== Debug ===\00"
@"str_56" = constant [3 x i8] c"%s\00"
@"str_57" = constant [2 x i8] c"\0a\00"
@"str_58" = constant [3 x i8] c"%s\00"
@"str_59" = constant [2 x i8] c"\0a\00"
@"str_60" = constant [9 x i8] c"Ponto { \00"
@"str_61" = constant [4 x i8] c"x: \00"
@"str_62" = constant [4 x i8] c"%ld\00"
@"str_63" = constant [3 x i8] c", \00"
@"str_64" = constant [4 x i8] c"y: \00"
@"str_65" = constant [4 x i8] c"%ld\00"
@"str_66" = constant [3 x i8] c" }\00"