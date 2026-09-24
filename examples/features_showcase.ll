; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"Point" = type {i64, i64}
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
  %".7" = bitcast [7 x i8]* @"str_0" to i8*
  %"name" = alloca i8*
  store i8* %".7", i8** %"name"
  %"version" = alloca i64
  store i64 1, i64* %"version"
  %".10" = bitcast [12 x i8]* @"str_1" to i8*
  %"name_load" = load i8*, i8** %"name"
  %".11" = bitcast [3 x i8]* @"str_2" to i8*
  %"version_load" = load i64, i64* %"version"
  %"fstr_num_buf_3" = alloca [32 x i8]
  %"fstr_num_i8_3" = bitcast [32 x i8]* %"fstr_num_buf_3" to i8*
  %".12" = bitcast [4 x i8]* @"str_3" to i8*
  %"fstr_snprintf_3" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"fstr_num_i8_3", i64 32, i8* %".12", i64 %"version_load")
  %".13" = bitcast [2 x i8]* @"str_4" to i8*
  %"fstr_len_str_0" = call i64 @"strlen"(i8* %".10")
  %"fstr_total_str_0" = add i64 1, %"fstr_len_str_0"
  %"fstr_len_var_1" = call i64 @"strlen"(i8* %"name_load")
  %"fstr_total_var_1" = add i64 %"fstr_total_str_0", %"fstr_len_var_1"
  %"fstr_len_str_2" = call i64 @"strlen"(i8* %".11")
  %"fstr_total_str_2" = add i64 %"fstr_total_var_1", %"fstr_len_str_2"
  %"fstr_len_num_3" = call i64 @"strlen"(i8* %"fstr_num_i8_3")
  %"fstr_total_num_3" = add i64 %"fstr_total_str_2", %"fstr_len_num_3"
  %"fstr_len_str_4" = call i64 @"strlen"(i8* %".13")
  %"fstr_total_str_4" = add i64 %"fstr_total_num_3", %"fstr_len_str_4"
  %"fstr_buf" = call i8* @"GC_malloc"(i64 %"fstr_total_str_4")
  %"fstr_first" = call i8* @"strcpy"(i8* %"fstr_buf", i8* %".10")
  %"fstr_cat_var_1" = call i8* @"strcat"(i8* %"fstr_buf", i8* %"name_load")
  %"fstr_cat_str_2" = call i8* @"strcat"(i8* %"fstr_buf", i8* %".11")
  %"fstr_cat_num_3" = call i8* @"strcat"(i8* %"fstr_buf", i8* %"fstr_num_i8_3")
  %"fstr_cat_str_4" = call i8* @"strcat"(i8* %"fstr_buf", i8* %".13")
  %".14" = bitcast [3 x i8]* @"str_5" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %"fstr_buf")
  %".15" = bitcast [2 x i8]* @"str_6" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [12 x i8]* @"str_7" to i8*
  %"msg" = alloca i8*
  store i8* %".16", i8** %"msg"
  %"msg_load" = load i8*, i8** %"msg"
  %"str_len" = call i64 @"strlen"(i8* %"msg_load")
  %"msg_len" = alloca i64
  store i64 %"str_len", i64* %"msg_len"
  %".19" = bitcast [16 x i8]* @"str_8" to i8*
  %"msg_len_load" = load i64, i64* %"msg_len"
  %"fstr_num_buf_1" = alloca [32 x i8]
  %"fstr_num_i8_1" = bitcast [32 x i8]* %"fstr_num_buf_1" to i8*
  %".20" = bitcast [4 x i8]* @"str_9" to i8*
  %"fstr_snprintf_1" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"fstr_num_i8_1", i64 32, i8* %".20", i64 %"msg_len_load")
  %"fstr_len_str_0.1" = call i64 @"strlen"(i8* %".19")
  %"fstr_total_str_0.1" = add i64 1, %"fstr_len_str_0.1"
  %"fstr_len_num_1" = call i64 @"strlen"(i8* %"fstr_num_i8_1")
  %"fstr_total_num_1" = add i64 %"fstr_total_str_0.1", %"fstr_len_num_1"
  %"fstr_buf.1" = call i8* @"GC_malloc"(i64 %"fstr_total_num_1")
  %"fstr_first.1" = call i8* @"strcpy"(i8* %"fstr_buf.1", i8* %".19")
  %"fstr_cat_num_1" = call i8* @"strcat"(i8* %"fstr_buf.1", i8* %"fstr_num_i8_1")
  %".21" = bitcast [3 x i8]* @"str_10" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %"fstr_buf.1")
  %".22" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %"msg_load.1" = load i8*, i8** %"msg"
  %".23" = bitcast [6 x i8]* @"str_12" to i8*
  %"str_strstr" = call i8* @"strstr"(i8* %"msg_load.1", i8* %".23")
  %"str_contains_res" = icmp ne i8* %"str_strstr", null
  br i1 %"str_contains_res", label %"if_then", label %"if_else"
if_then:
  %".25" = bitcast [26 x i8]* @"str_13" to i8*
  %".26" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".26", i8* %".25")
  %".27" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".27")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"msg_load.2" = load i8*, i8** %"msg"
  %".30" = bitcast [6 x i8]* @"str_16" to i8*
  %"starts_len" = call i64 @"strlen"(i8* %".30")
  %"starts_cmp" = call i32 @"strncmp"(i8* %"msg_load.2", i8* %".30", i64 %"starts_len")
  %"starts_res" = icmp eq i32 %"starts_cmp", 0
  br i1 %"starts_res", label %"if_then.1", label %"if_else.1"
if_then.1:
  %".32" = bitcast [29 x i8]* @"str_17" to i8*
  %".33" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %".32")
  %".34" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".34")
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"msg_load.3" = load i8*, i8** %"msg"
  %"case_len" = call i64 @"strlen"(i8* %"msg_load.3")
  %"case_total" = add i64 %"case_len", 1
  %"case_buf" = call i8* @"GC_malloc"(i64 %"case_total")
  br label %"case_loop"
case_loop:
  %"case_i" = phi  i64 [0, %"if_end.1"], [%"case_next", %"case_loop"]
  %"case_char_ptr" = getelementptr i8, i8* %"case_buf", i64 %"case_i"
  %"case_char" = load i8, i8* %"case_char_ptr"
  %"is_ge_a" = icmp sge i8 %"case_char", 97
  %"is_le_z" = icmp sle i8 %"case_char", 122
  %"is_alpha" = and i1 %"is_ge_a", %"is_le_z"
  %"new_char" = add i8 %"case_char", -32
  %"final_char" = select  i1 %"is_alpha", i8 %"new_char", i8 %"case_char"
  store i8 %"final_char", i8* %"case_char_ptr"
  %"case_next" = add i64 %"case_i", 1
  %"case_cond" = icmp slt i64 %"case_next", %"case_len"
  br i1 %"case_cond", label %"case_loop", label %"case_end"
case_end:
  %"case_null_ptr" = getelementptr i8, i8* %"case_buf", i64 %"case_len"
  store i8 0, i8* %"case_null_ptr"
  %"upper_msg" = alloca i64
  %"str_to_int_call" = call i64 @"atoi"(i8* %"case_buf")
  store i64 %"str_to_int_call", i64* %"upper_msg"
  %"upper_msg_load" = load i64, i64* %"upper_msg"
  %".42" = bitcast [4 x i8]* @"str_20" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".42", i64 %"upper_msg_load")
  %".43" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".43")
  %"x" = alloca i64
  store i64 5, i64* %"x"
  %"__chain_0_0" = alloca i64
  store i64 0, i64* %"__chain_0_0"
  %"x_load" = load i64, i64* %"x"
  %"__chain_0_1" = alloca i64
  store i64 %"x_load", i64* %"__chain_0_1"
  %"__chain_0_2" = alloca i64
  store i64 10, i64* %"__chain_0_2"
  %"__chain_0_0_load" = load i64, i64* %"__chain_0_0"
  %"__chain_0_1_load" = load i64, i64* %"__chain_0_1"
  %"icmp" = icmp slt i64 %"__chain_0_0_load", %"__chain_0_1_load"
  %"__chain_0_1_load.1" = load i64, i64* %"__chain_0_1"
  %"__chain_0_2_load" = load i64, i64* %"__chain_0_2"
  %"icmp.1" = icmp slt i64 %"__chain_0_1_load.1", %"__chain_0_2_load"
  %"chain_and_1" = and i1 %"icmp", %"icmp.1"
  br i1 %"chain_and_1", label %"if_then.2", label %"if_else.2"
if_then.2:
  %".49" = bitcast [22 x i8]* @"str_22" to i8*
  %".50" = bitcast [3 x i8]* @"str_23" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".50", i8* %".49")
  %".51" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".51")
  br label %"if_end.2"
if_else.2:
  br label %"if_end.2"
if_end.2:
  %"status_code" = alloca i64
  store i64 404, i64* %"status_code"
  %"status_code_load" = load i64, i64* %"status_code"
  switch i64 %"status_code_load", label %"match_default" [i64 200, label %"match_case" i64 404, label %"match_case.1" i64 500, label %"match_case.2"]
match_end:
  %"match_res" = phi  i8* [%".56", %"match_case"], [%".58", %"match_case.1"], [%".60", %"match_case.2"], [%".62", %"match_default"]
  %"status_msg" = alloca i64
  %"str_to_int_call.1" = call i64 @"atoi"(i8* %"match_res")
  store i64 %"str_to_int_call.1", i64* %"status_msg"
  %"status_msg_load" = load i64, i64* %"status_msg"
  %".65" = bitcast [4 x i8]* @"str_29" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".65", i64 %"status_msg_load")
  %".66" = bitcast [2 x i8]* @"str_30" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".66")
  %".67" = bitcast [4 x i8]* @"str_31" to i8*
  %"command" = alloca i8*
  store i8* %".67", i8** %"command"
  %"command_load" = load i8*, i8** %"command"
  %".69" = bitcast [6 x i8]* @"str_32" to i8*
  %"strcmp_call" = call i32 @"strcmp"(i8* %"command_load", i8* %".69")
  %"str_eq" = icmp eq i32 %"strcmp_call", 0
  br i1 %"str_eq", label %"match_str_case", label %"match_str_next"
match_default:
  %".62" = bitcast [8 x i8]* @"str_28" to i8*
  br label %"match_end"
match_case:
  %".56" = bitcast [3 x i8]* @"str_25" to i8*
  br label %"match_end"
match_case.1:
  %".58" = bitcast [10 x i8]* @"str_26" to i8*
  br label %"match_end"
match_case.2:
  %".60" = bitcast [13 x i8]* @"str_27" to i8*
  br label %"match_end"
match_str_end:
  %"match_str_res" = phi  i64 [0, %"match_str_case"], [0, %"match_str_case.1"], [0, %"match_str_case.2"], [0, %"match_str_next.2"]
  %"point_lit" = alloca %"Point"
  %"x_ptr" = getelementptr %"Point", %"Point"* %"point_lit", i32 0, i32 0
  store i64 10, i64* %"x_ptr"
  %"y_ptr" = getelementptr %"Point", %"Point"* %"point_lit", i32 0, i32 1
  store i64 20, i64* %"y_ptr"
  %"p" = alloca %"Point"*
  store %"Point"* %"point_lit", %"Point"** %"p"
  %"p_load" = load %"Point"*, %"Point"** %"p"
  br label %"match_struct_case"
match_str_case:
  %".71" = bitcast [12 x i8]* @"str_33" to i8*
  %".72" = bitcast [3 x i8]* @"str_34" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".72", i8* %".71")
  %".73" = bitcast [2 x i8]* @"str_35" to i8*
  %"print_nl.7" = call i32 (i8*, ...) @"printf"(i8* %".73")
  br label %"match_str_end"
match_str_next:
  %".75" = bitcast [4 x i8]* @"str_36" to i8*
  %"strcmp_call.1" = call i32 @"strcmp"(i8* %"command_load", i8* %".75")
  %"str_eq.1" = icmp eq i32 %"strcmp_call.1", 0
  br i1 %"str_eq.1", label %"match_str_case.1", label %"match_str_next.1"
match_str_case.1:
  %".77" = bitcast [11 x i8]* @"str_37" to i8*
  %".78" = bitcast [3 x i8]* @"str_38" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".78", i8* %".77")
  %".79" = bitcast [2 x i8]* @"str_39" to i8*
  %"print_nl.8" = call i32 (i8*, ...) @"printf"(i8* %".79")
  br label %"match_str_end"
match_str_next.1:
  %".81" = bitcast [5 x i8]* @"str_40" to i8*
  %"strcmp_call.2" = call i32 @"strcmp"(i8* %"command_load", i8* %".81")
  %"str_eq.2" = icmp eq i32 %"strcmp_call.2", 0
  br i1 %"str_eq.2", label %"match_str_case.2", label %"match_str_next.2"
match_str_case.2:
  %".83" = bitcast [11 x i8]* @"str_41" to i8*
  %".84" = bitcast [3 x i8]* @"str_42" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".84", i8* %".83")
  %".85" = bitcast [2 x i8]* @"str_43" to i8*
  %"print_nl.9" = call i32 (i8*, ...) @"printf"(i8* %".85")
  br label %"match_str_end"
match_str_next.2:
  %".87" = bitcast [16 x i8]* @"str_44" to i8*
  %".88" = bitcast [3 x i8]* @"str_45" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".88", i8* %".87")
  %".89" = bitcast [2 x i8]* @"str_46" to i8*
  %"print_nl.10" = call i32 (i8*, ...) @"printf"(i8* %".89")
  br label %"match_str_end"
match_struct_end:
  %"match_struct_res" = phi  i64 [%"add", %"match_struct_case"], [0, %"match_struct_next"]
  %"sum" = alloca i64
  store i64 %"match_struct_res", i64* %"sum"
  %".102" = bitcast [22 x i8]* @"str_47" to i8*
  %"sum_load" = load i64, i64* %"sum"
  %"fstr_num_buf_1.1" = alloca [32 x i8]
  %"fstr_num_i8_1.1" = bitcast [32 x i8]* %"fstr_num_buf_1.1" to i8*
  %".103" = bitcast [4 x i8]* @"str_48" to i8*
  %"fstr_snprintf_1.1" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"fstr_num_i8_1.1", i64 32, i8* %".103", i64 %"sum_load")
  %"fstr_len_str_0.2" = call i64 @"strlen"(i8* %".102")
  %"fstr_total_str_0.2" = add i64 1, %"fstr_len_str_0.2"
  %"fstr_len_num_1.1" = call i64 @"strlen"(i8* %"fstr_num_i8_1.1")
  %"fstr_total_num_1.1" = add i64 %"fstr_total_str_0.2", %"fstr_len_num_1.1"
  %"fstr_buf.2" = call i8* @"GC_malloc"(i64 %"fstr_total_num_1.1")
  %"fstr_first.2" = call i8* @"strcpy"(i8* %"fstr_buf.2", i8* %".102")
  %"fstr_cat_num_1.1" = call i8* @"strcat"(i8* %"fstr_buf.2", i8* %"fstr_num_i8_1.1")
  %".104" = bitcast [3 x i8]* @"str_49" to i8*
  %"print_call.11" = call i32 (i8*, ...) @"printf"(i8* %".104", i8* %"fstr_buf.2")
  %".105" = bitcast [2 x i8]* @"str_50" to i8*
  %"print_nl.11" = call i32 (i8*, ...) @"printf"(i8* %".105")
  %"total" = alloca i64
  store i64 0, i64* %"total"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
match_struct_case:
  %".95" = getelementptr %"Point", %"Point"* %"p_load", i32 0, i32 0
  %"bind_val" = load i64, i64* %".95"
  %"px" = alloca i64
  store i64 %"bind_val", i64* %"px"
  %".97" = getelementptr %"Point", %"Point"* %"p_load", i32 0, i32 1
  %"bind_val.1" = load i64, i64* %".97"
  %"py" = alloca i64
  store i64 %"bind_val.1", i64* %"py"
  %"px_load" = load i64, i64* %"px"
  %"py_load" = load i64, i64* %"py"
  %"add" = add i64 %"px_load", %"py_load"
  br label %"match_struct_end"
match_struct_next:
  br label %"match_struct_end"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp.2" = icmp slt i64 %"i_load", 5
  br i1 %"icmp.2", label %"while_body", label %"while_end"
while_body:
  %"total_load" = load i64, i64* %"total"
  %"i_load.1" = load i64, i64* %"i"
  %"add.1" = add i64 %"total_load", %"i_load.1"
  store i64 %"add.1", i64* %"total"
  %"i_load.2" = load i64, i64* %"i"
  %"add.2" = add i64 %"i_load.2", 1
  store i64 %"add.2", i64* %"i"
  br label %"while_cond"
while_end:
  %".113" = bitcast [12 x i8]* @"str_51" to i8*
  %"total_load.1" = load i64, i64* %"total"
  %"fstr_num_buf_1.2" = alloca [32 x i8]
  %"fstr_num_i8_1.2" = bitcast [32 x i8]* %"fstr_num_buf_1.2" to i8*
  %".114" = bitcast [4 x i8]* @"str_52" to i8*
  %"fstr_snprintf_1.2" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"fstr_num_i8_1.2", i64 32, i8* %".114", i64 %"total_load.1")
  %"fstr_len_str_0.3" = call i64 @"strlen"(i8* %".113")
  %"fstr_total_str_0.3" = add i64 1, %"fstr_len_str_0.3"
  %"fstr_len_num_1.2" = call i64 @"strlen"(i8* %"fstr_num_i8_1.2")
  %"fstr_total_num_1.2" = add i64 %"fstr_total_str_0.3", %"fstr_len_num_1.2"
  %"fstr_buf.3" = call i8* @"GC_malloc"(i64 %"fstr_total_num_1.2")
  %"fstr_first.3" = call i8* @"strcpy"(i8* %"fstr_buf.3", i8* %".113")
  %"fstr_cat_num_1.2" = call i8* @"strcat"(i8* %"fstr_buf.3", i8* %"fstr_num_i8_1.2")
  %".115" = bitcast [3 x i8]* @"str_53" to i8*
  %"print_call.12" = call i32 (i8*, ...) @"printf"(i8* %".115", i8* %"fstr_buf.3")
  %".116" = bitcast [2 x i8]* @"str_54" to i8*
  %"print_nl.12" = call i32 (i8*, ...) @"printf"(i8* %".116")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [7 x i8] c"Lumina\00"
@"str_1" = constant [12 x i8] c"Welcome to \00"
@"str_2" = constant [3 x i8] c" v\00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"!\00"
@"str_5" = constant [3 x i8] c"%s\00"
@"str_6" = constant [2 x i8] c"\0a\00"
@"str_7" = constant [12 x i8] c"Hello World\00"
@"str_8" = constant [16 x i8] c"Length of msg: \00"
@"str_9" = constant [4 x i8] c"%ld\00"
@"str_10" = constant [3 x i8] c"%s\00"
@"str_11" = constant [2 x i8] c"\0a\00"
@"str_12" = constant [6 x i8] c"World\00"
@"str_13" = constant [26 x i8] c"Contains 'World' is true!\00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c"\0a\00"
@"str_16" = constant [6 x i8] c"Hello\00"
@"str_17" = constant [29 x i8] c"Starts with 'Hello' is true!\00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c"\0a\00"
@"str_20" = constant [4 x i8] c"%ld\00"
@"str_21" = constant [2 x i8] c"\0a\00"
@"str_22" = constant [22 x i8] c"x is between 0 and 10\00"
@"str_23" = constant [3 x i8] c"%s\00"
@"str_24" = constant [2 x i8] c"\0a\00"
@"str_25" = constant [3 x i8] c"OK\00"
@"str_26" = constant [10 x i8] c"Not Found\00"
@"str_27" = constant [13 x i8] c"Server Error\00"
@"str_28" = constant [8 x i8] c"Unknown\00"
@"str_29" = constant [4 x i8] c"%ld\00"
@"str_30" = constant [2 x i8] c"\0a\00"
@"str_31" = constant [4 x i8] c"run\00"
@"str_32" = constant [6 x i8] c"build\00"
@"str_33" = constant [12 x i8] c"Building...\00"
@"str_34" = constant [3 x i8] c"%s\00"
@"str_35" = constant [2 x i8] c"\0a\00"
@"str_36" = constant [4 x i8] c"run\00"
@"str_37" = constant [11 x i8] c"Running...\00"
@"str_38" = constant [3 x i8] c"%s\00"
@"str_39" = constant [2 x i8] c"\0a\00"
@"str_40" = constant [5 x i8] c"test\00"
@"str_41" = constant [11 x i8] c"Testing...\00"
@"str_42" = constant [3 x i8] c"%s\00"
@"str_43" = constant [2 x i8] c"\0a\00"
@"str_44" = constant [16 x i8] c"Unknown command\00"
@"str_45" = constant [3 x i8] c"%s\00"
@"str_46" = constant [2 x i8] c"\0a\00"
@"str_47" = constant [22 x i8] c"Sum of point coords: \00"
@"str_48" = constant [4 x i8] c"%ld\00"
@"str_49" = constant [3 x i8] c"%s\00"
@"str_50" = constant [2 x i8] c"\0a\00"
@"str_51" = constant [12 x i8] c"Sum 0..5 = \00"
@"str_52" = constant [4 x i8] c"%ld\00"
@"str_53" = constant [3 x i8] c"%s\00"
@"str_54" = constant [2 x i8] c"\0a\00"