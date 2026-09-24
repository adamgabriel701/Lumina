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
define void @"db_load"()
{
db_load_entry:
  br label %"db_load_body"
db_load_body:
  %".3" = bitcast [14 x i8]* @"str_0" to i8*
  %".4" = bitcast [2 x i8]* @"str_1" to i8*
  %"rf_fopen" = call i8* @"fopen"(i8* %".3", i8* %".4")
  %"rf_fp_int" = ptrtoint i8* %"rf_fopen" to i64
  %"rf_is_null" = icmp eq i64 %"rf_fp_int", 0
  br i1 %"rf_is_null", label %"rf_null", label %"rf_ok"
rf_null:
  %".6" = bitcast [1 x i8]* @"str_2" to i8*
  br label %"rf_end"
rf_ok:
  %"rf_seek_end" = call i32 @"fseek"(i8* %"rf_fopen", i64 0, i32 2)
  %"rf_size" = call i64 @"ftell"(i8* %"rf_fopen")
  %"rf_seek_set" = call i32 @"fseek"(i8* %"rf_fopen", i64 0, i32 0)
  %"rf_size_plus" = add i64 %"rf_size", 1
  %"rf_buf" = call i8* @"GC_malloc"(i64 %"rf_size_plus")
  %"rf_fread" = call i64 @"fread"(i8* %"rf_buf", i64 1, i64 %"rf_size", i8* %"rf_fopen")
  %"rf_end_ptr" = getelementptr i8, i8* %"rf_buf", i64 %"rf_size"
  store i8 0, i8* %"rf_end_ptr"
  %"rf_fclose" = call i32 @"fclose"(i8* %"rf_fopen")
  br label %"rf_end"
rf_end:
  %"rf_result" = phi  i8* [%".6", %"rf_null"], [%"rf_buf", %"rf_ok"]
  ret void
}

define void @"db_save"()
{
db_save_entry:
  br label %"db_save_body"
db_save_body:
  %".3" = bitcast [14 x i8]* @"str_3" to i8*
  %".4" = bitcast [1 x i8]* @"str_4" to i8*
  %".5" = bitcast [2 x i8]* @"str_5" to i8*
  %"wf_fopen" = call i8* @"fopen"(i8* %".3", i8* %".5")
  %"wf_fputs" = call i32 @"fputs"(i8* %".4", i8* %"wf_fopen")
  %"wf_fclose" = call i32 @"fclose"(i8* %"wf_fopen")
  ret void
}

define void @"db_set"(i8* %".1", i8* %".2")
{
db_set_entry:
  %"key" = alloca i8*
  store i8* %".1", i8** %"key"
  %"val" = alloca i8*
  store i8* %".2", i8** %"val"
  br label %"db_set_body"
db_set_body:
  %".7" = bitcast [1 x i8]* @"str_6" to i8*
  %"key_load" = load i8*, i8** %"key"
  %"sconcat_len1" = call i64 @"strlen"(i8* %".7")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"key_load")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".7")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"key_load")
  %".8" = bitcast [2 x i8]* @"str_7" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".8")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".8")
  %"val_load" = load i8*, i8** %"val"
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %"val_load")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %"val_load")
  %".9" = bitcast [2 x i8]* @"str_8" to i8*
  %"sconcat_len1.3" = call i64 @"strlen"(i8* %"sconcat_buf.2")
  %"sconcat_len2.3" = call i64 @"strlen"(i8* %".9")
  %"sconcat_sum.3" = add i64 %"sconcat_len1.3", %"sconcat_len2.3"
  %"sconcat_total.3" = add i64 %"sconcat_sum.3", 1
  %"sconcat_buf.3" = call i8* @"GC_malloc"(i64 %"sconcat_total.3")
  %"sconcat_cpy.3" = call i8* @"strcpy"(i8* %"sconcat_buf.3", i8* %"sconcat_buf.2")
  %"sconcat_cat.3" = call i8* @"strcat"(i8* %"sconcat_buf.3", i8* %".9")
  call void @"db_save"()
  %".10" = bitcast [14 x i8]* @"str_9" to i8*
  %".11" = bitcast [3 x i8]* @"str_10" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".10")
  %"key_load.1" = load i8*, i8** %"key"
  %".12" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %".13" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".13", i8* %"key_load.1")
  %".14" = bitcast [3 x i8]* @"str_13" to i8*
  %".15" = bitcast [2 x i8]* @"str_14" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [3 x i8]* @"str_15" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".16", i8* %".14")
  %"val_load.1" = load i8*, i8** %"val"
  %".17" = bitcast [2 x i8]* @"str_16" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [3 x i8]* @"str_17" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".18", i8* %"val_load.1")
  %".19" = bitcast [2 x i8]* @"str_18" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".19")
  ret void
}

define i8* @"db_get"(i8* %".1")
{
db_get_entry:
  %"key" = alloca i8*
  store i8* %".1", i8** %"key"
  br label %"db_get_body"
db_get_body:
  %".5" = bitcast [1 x i8]* @"str_19" to i8*
  %"len_str" = call i64 @"strlen"(i8* %".5")
  %"mem_len" = alloca i64
  store i64 %"len_str", i64* %"mem_len"
  %"key_load" = load i8*, i8** %"key"
  %"len_str.1" = call i64 @"strlen"(i8* %"key_load")
  %"key_len" = alloca i64
  store i64 %"len_str.1", i64* %"key_len"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"mem_len_load" = load i64, i64* %"mem_len"
  %"icmp" = icmp slt i64 %"i_load", %"mem_len_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"is_match" = alloca i64
  store i64 1, i64* %"is_match"
  %"j" = alloca i64
  store i64 0, i64* %"j"
  br label %"while_cond.1"
while_end:
  %".57" = bitcast [10 x i8]* @"str_26" to i8*
  ret i8* %".57"
while_cond.1:
  %"j_load" = load i64, i64* %"j"
  %"key_len_load" = load i64, i64* %"key_len"
  %"icmp.1" = icmp slt i64 %"j_load", %"key_len_load"
  br i1 %"icmp.1", label %"while_body.1", label %"while_end.1"
while_body.1:
  %".15" = bitcast [1 x i8]* @"str_20" to i8*
  %"i_load.1" = load i64, i64* %"i"
  %"j_load.1" = load i64, i64* %"j"
  %"add" = add i64 %"i_load.1", %"j_load.1"
  %".16" = getelementptr i8, i8* %".15", i64 %"add"
  %"ptr_idx_load" = load i8, i8* %".16"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"key_load.1" = load i8*, i8** %"key"
  %"j_load.2" = load i64, i64* %"j"
  %".17" = getelementptr i8, i8* %"key_load.1", i64 %"j_load.2"
  %"ptr_idx_load.1" = load i8, i8* %".17"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"icmp.2" = icmp ne i64 %"idx_sext", %"idx_sext.1"
  br i1 %"icmp.2", label %"if_then", label %"if_else"
while_end.1:
  %"is_match_load" = load i64, i64* %"is_match"
  %"icmp.3" = icmp eq i64 %"is_match_load", 1
  br i1 %"icmp.3", label %"and_rhs", label %"and_end"
if_then:
  store i64 0, i64* %"is_match"
  br label %"while_end.1"
if_else:
  br label %"if_end"
if_end:
  %"j_load.3" = load i64, i64* %"j"
  %"add.1" = add i64 %"j_load.3", 1
  store i64 %"add.1", i64* %"j"
  br label %"while_cond.1"
and_rhs:
  %".25" = bitcast [1 x i8]* @"str_21" to i8*
  %"i_load.2" = load i64, i64* %"i"
  %"key_len_load.1" = load i64, i64* %"key_len"
  %"add.2" = add i64 %"i_load.2", %"key_len_load.1"
  %".26" = getelementptr i8, i8* %".25", i64 %"add.2"
  %"ptr_idx_load.2" = load i8, i8* %".26"
  %"idx_sext.2" = sext i8 %"ptr_idx_load.2" to i64
  %"icmp.4" = icmp eq i64 %"idx_sext.2", 61
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_end.1"], [%"icmp.4", %"and_rhs"]
  br i1 %"and_result", label %"if_then.1", label %"if_else.1"
if_then.1:
  %".29" = bitcast [1 x i8]* @"str_22" to i8*
  %"val" = alloca i8*
  store i8* %".29", i8** %"val"
  %"i_load.3" = load i64, i64* %"i"
  %"key_len_load.2" = load i64, i64* %"key_len"
  %"add.3" = add i64 %"i_load.3", %"key_len_load.2"
  %"add.4" = add i64 %"add.3", 1
  %"k" = alloca i64
  store i64 %"add.4", i64* %"k"
  br label %"while_cond.2"
if_else.1:
  br label %"if_end.1"
if_end.1:
  br label %"while_cond.3"
while_cond.2:
  %"k_load" = load i64, i64* %"k"
  %"mem_len_load.1" = load i64, i64* %"mem_len"
  %"icmp.5" = icmp slt i64 %"k_load", %"mem_len_load.1"
  br i1 %"icmp.5", label %"and_rhs.1", label %"and_end.1"
while_body.2:
  %"val_load" = load i8*, i8** %"val"
  %".38" = bitcast [1 x i8]* @"str_24" to i8*
  %"k_load.2" = load i64, i64* %"k"
  %".39" = getelementptr i8, i8* %".38", i64 %"k_load.2"
  %"ptr_idx_load.4" = load i8, i8* %".39"
  %"idx_sext.4" = sext i8 %"ptr_idx_load.4" to i64
  %"chr_trunc" = trunc i64 %"idx_sext.4" to i8
  %"chr_buf" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc", i8* %"chr_buf"
  %"chr_null_ptr" = getelementptr i8, i8* %"chr_buf", i64 1
  store i8 0, i8* %"chr_null_ptr"
  %"sconcat_len1" = call i64 @"strlen"(i8* %"val_load")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"chr_buf")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"val_load")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"chr_buf")
  store i8* %"sconcat_buf", i8** %"val"
  %"k_load.3" = load i64, i64* %"k"
  %"add.5" = add i64 %"k_load.3", 1
  store i64 %"add.5", i64* %"k"
  br label %"while_cond.2"
while_end.2:
  %"val_load.1" = load i8*, i8** %"val"
  ret i8* %"val_load.1"
and_rhs.1:
  %".34" = bitcast [1 x i8]* @"str_23" to i8*
  %"k_load.1" = load i64, i64* %"k"
  %".35" = getelementptr i8, i8* %".34", i64 %"k_load.1"
  %"ptr_idx_load.3" = load i8, i8* %".35"
  %"idx_sext.3" = sext i8 %"ptr_idx_load.3" to i64
  %"icmp.6" = icmp ne i64 %"idx_sext.3", 10
  br label %"and_end.1"
and_end.1:
  %"and_result.1" = phi  i1 [0, %"while_cond.2"], [%"icmp.6", %"and_rhs.1"]
  br i1 %"and_result.1", label %"while_body.2", label %"while_end.2"
while_cond.3:
  %"i_load.4" = load i64, i64* %"i"
  %"mem_len_load.2" = load i64, i64* %"mem_len"
  %"icmp.7" = icmp slt i64 %"i_load.4", %"mem_len_load.2"
  br i1 %"icmp.7", label %"and_rhs.2", label %"and_end.2"
while_body.3:
  %"i_load.6" = load i64, i64* %"i"
  %"add.6" = add i64 %"i_load.6", 1
  store i64 %"add.6", i64* %"i"
  br label %"while_cond.3"
while_end.3:
  %"i_load.7" = load i64, i64* %"i"
  %"add.7" = add i64 %"i_load.7", 1
  store i64 %"add.7", i64* %"i"
  br label %"while_cond"
and_rhs.2:
  %".49" = bitcast [1 x i8]* @"str_25" to i8*
  %"i_load.5" = load i64, i64* %"i"
  %".50" = getelementptr i8, i8* %".49", i64 %"i_load.5"
  %"ptr_idx_load.5" = load i8, i8* %".50"
  %"idx_sext.5" = sext i8 %"ptr_idx_load.5" to i64
  %"icmp.8" = icmp ne i64 %"idx_sext.5", 10
  br label %"and_end.2"
and_end.2:
  %"and_result.2" = phi  i1 [0, %"while_cond.3"], [%"icmp.8", %"and_rhs.2"]
  br i1 %"and_result.2", label %"while_body.3", label %"while_end.3"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [27 x i8]* @"str_27" to i8*
  %".8" = bitcast [3 x i8]* @"str_28" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_29" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  call void @"db_load"()
  %".10" = bitcast [5 x i8]* @"str_30" to i8*
  %".11" = bitcast [6 x i8]* @"str_31" to i8*
  call void @"db_set"(i8* %".10", i8* %".11")
  %".12" = bitcast [5 x i8]* @"str_32" to i8*
  %".13" = bitcast [5 x i8]* @"str_33" to i8*
  call void @"db_set"(i8* %".12", i8* %".13")
  %".14" = bitcast [5 x i8]* @"str_34" to i8*
  %".15" = bitcast [7 x i8]* @"str_35" to i8*
  call void @"db_set"(i8* %".14", i8* %".15")
  %".16" = bitcast [5 x i8]* @"str_36" to i8*
  %"db_get_call" = call i8* @"db_get"(i8* %".16")
  %"u" = alloca i8*
  store i8* %"db_get_call", i8** %"u"
  %".18" = bitcast [5 x i8]* @"str_37" to i8*
  %"db_get_call.1" = call i8* @"db_get"(i8* %".18")
  %"p" = alloca i8*
  store i8* %"db_get_call.1", i8** %"p"
  %".20" = bitcast [5 x i8]* @"str_38" to i8*
  %"db_get_call.2" = call i8* @"db_get"(i8* %".20")
  %"l" = alloca i8*
  store i8* %"db_get_call.2", i8** %"l"
  %".22" = bitcast [6 x i8]* @"str_39" to i8*
  %".23" = bitcast [3 x i8]* @"str_40" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %".22")
  %"u_load" = load i8*, i8** %"u"
  %".24" = bitcast [2 x i8]* @"str_41" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [3 x i8]* @"str_42" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %"u_load")
  %".26" = bitcast [2 x i8]* @"str_43" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %".27" = bitcast [6 x i8]* @"str_44" to i8*
  %".28" = bitcast [3 x i8]* @"str_45" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %"p_load" = load i8*, i8** %"p"
  %".29" = bitcast [2 x i8]* @"str_46" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".29")
  %".30" = bitcast [3 x i8]* @"str_47" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".30", i8* %"p_load")
  %".31" = bitcast [2 x i8]* @"str_48" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".31")
  %".32" = bitcast [6 x i8]* @"str_49" to i8*
  %".33" = bitcast [3 x i8]* @"str_50" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %".32")
  %"l_load" = load i8*, i8** %"l"
  %".34" = bitcast [2 x i8]* @"str_51" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".34")
  %".35" = bitcast [3 x i8]* @"str_52" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".35", i8* %"l_load")
  %".36" = bitcast [2 x i8]* @"str_53" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
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

@"str_0" = constant [14 x i8] c"lumina_db.txt\00"
declare i8* @"fopen"(i8* %".1", i8* %".2")

declare i32 @"fseek"(i8* %".1", i64 %".2", i32 %".3")

declare i64 @"ftell"(i8* %".1")

declare i64 @"fread"(i8* %".1", i64 %".2", i64 %".3", i8* %".4")

declare i32 @"fclose"(i8* %".1")

@"str_1" = constant [2 x i8] c"r\00"
@"str_2" = constant [1 x i8] c"\00"
@"str_3" = constant [14 x i8] c"lumina_db.txt\00"
@"str_4" = constant [1 x i8] c"\00"
declare i32 @"fputs"(i8* %".1", i8* %".2")

@"str_5" = constant [2 x i8] c"w\00"
@"str_6" = constant [1 x i8] c"\00"
@"str_7" = constant [2 x i8] c"=\00"
@"str_8" = constant [2 x i8] c"\0a\00"
@"str_9" = constant [14 x i8] c"\e2\9c\85 Inserido:\00"
@"str_10" = constant [3 x i8] c"%s\00"
@"str_11" = constant [2 x i8] c" \00"
@"str_12" = constant [3 x i8] c"%s\00"
@"str_13" = constant [3 x i8] c"->\00"
@"str_14" = constant [2 x i8] c" \00"
@"str_15" = constant [3 x i8] c"%s\00"
@"str_16" = constant [2 x i8] c" \00"
@"str_17" = constant [3 x i8] c"%s\00"
@"str_18" = constant [2 x i8] c"\0a\00"
@"str_19" = constant [1 x i8] c"\00"
@"str_20" = constant [1 x i8] c"\00"
@"str_21" = constant [1 x i8] c"\00"
@"str_22" = constant [1 x i8] c"\00"
@"str_23" = constant [1 x i8] c"\00"
@"str_24" = constant [1 x i8] c"\00"
@"str_25" = constant [1 x i8] c"\00"
@"str_26" = constant [10 x i8] c"NOT_FOUND\00"
@"str_27" = constant [27 x i8] c"\f0\9f\9a\80 LuminaDB iniciando...\00"
@"str_28" = constant [3 x i8] c"%s\00"
@"str_29" = constant [2 x i8] c"\0a\00"
@"str_30" = constant [5 x i8] c"user\00"
@"str_31" = constant [6 x i8] c"admin\00"
@"str_32" = constant [5 x i8] c"pass\00"
@"str_33" = constant [5 x i8] c"1234\00"
@"str_34" = constant [5 x i8] c"lang\00"
@"str_35" = constant [7 x i8] c"Lumina\00"
@"str_36" = constant [5 x i8] c"user\00"
@"str_37" = constant [5 x i8] c"pass\00"
@"str_38" = constant [5 x i8] c"lang\00"
@"str_39" = constant [6 x i8] c"User:\00"
@"str_40" = constant [3 x i8] c"%s\00"
@"str_41" = constant [2 x i8] c" \00"
@"str_42" = constant [3 x i8] c"%s\00"
@"str_43" = constant [2 x i8] c"\0a\00"
@"str_44" = constant [6 x i8] c"Pass:\00"
@"str_45" = constant [3 x i8] c"%s\00"
@"str_46" = constant [2 x i8] c" \00"
@"str_47" = constant [3 x i8] c"%s\00"
@"str_48" = constant [2 x i8] c"\0a\00"
@"str_49" = constant [6 x i8] c"Lang:\00"
@"str_50" = constant [3 x i8] c"%s\00"
@"str_51" = constant [2 x i8] c" \00"
@"str_52" = constant [3 x i8] c"%s\00"
@"str_53" = constant [2 x i8] c"\0a\00"