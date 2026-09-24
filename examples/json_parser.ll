; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"JsonField" = type {i8*, i64, i8*, i64}
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
define i8* @"parse_json"(i8* %".1")
{
parse_json_entry:
  %"json_str" = alloca i8*
  store i8* %".1", i8** %"json_str"
  br label %"parse_json_body"
parse_json_body:
  %"json_str_load" = load i8*, i8** %"json_str"
  %"len_str" = call i64 @"strlen"(i8* %"json_str_load")
  %"len" = alloca i64
  store i64 %"len_str", i64* %"len"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"len_load" = load i64, i64* %"len"
  %"icmp" = icmp slt i64 %"i_load", %"len_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"json_str_load.1" = load i8*, i8** %"json_str"
  %"i_load.1" = load i64, i64* %"i"
  %".9" = getelementptr i8, i8* %"json_str_load.1", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".9"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"c" = alloca i64
  store i64 %"idx_sext", i64* %"c"
  %"c_load" = load i64, i64* %"c"
  %"icmp.1" = icmp eq i64 %"c_load", 123
  br i1 %"icmp.1", label %"or_end", label %"or_rhs"
while_end:
  %".20" = bitcast [1 x i8]* @"str_0" to i8*
  %"current_key" = alloca i8*
  store i8* %".20", i8** %"current_key"
  %".22" = bitcast [1 x i8]* @"str_1" to i8*
  %"current_val" = alloca i8*
  store i8* %".22", i8** %"current_val"
  %"in_key" = alloca i64
  store i64 0, i64* %"in_key"
  %"in_val" = alloca i64
  store i64 0, i64* %"in_val"
  %"val_type" = alloca i64
  store i64 0, i64* %"val_type"
  %".27" = bitcast [30 x i8]* @"str_2" to i8*
  %".28" = bitcast [3 x i8]* @"str_3" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".28", i8* %".27")
  %".29" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".29")
  br label %"while_cond.1"
or_rhs:
  %"c_load.1" = load i64, i64* %"c"
  %"icmp.2" = icmp eq i64 %"c_load.1", 32
  br label %"or_end"
or_end:
  %"or_result" = phi  i1 [1, %"while_body"], [%"icmp.2", %"or_rhs"]
  br i1 %"or_result", label %"or_end.1", label %"or_rhs.1"
or_rhs.1:
  %"c_load.2" = load i64, i64* %"c"
  %"icmp.3" = icmp eq i64 %"c_load.2", 10
  br label %"or_end.1"
or_end.1:
  %"or_result.1" = phi  i1 [1, %"or_end"], [%"icmp.3", %"or_rhs.1"]
  br i1 %"or_result.1", label %"if_then", label %"if_else"
if_then:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"if_end"
if_else:
  br label %"while_end"
if_end:
  br label %"while_cond"
while_cond.1:
  %"i_load.3" = load i64, i64* %"i"
  %"len_load.1" = load i64, i64* %"len"
  %"icmp.4" = icmp slt i64 %"i_load.3", %"len_load.1"
  br i1 %"icmp.4", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"json_str_load.2" = load i8*, i8** %"json_str"
  %"i_load.4" = load i64, i64* %"i"
  %".32" = getelementptr i8, i8* %"json_str_load.2", i64 %"i_load.4"
  %"ptr_idx_load.1" = load i8, i8* %".32"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"c.1" = alloca i64
  store i64 %"idx_sext.1", i64* %"c.1"
  %"c_load.3" = load i64, i64* %"c.1"
  %"icmp.5" = icmp eq i64 %"c_load.3", 34
  br i1 %"icmp.5", label %"if_then.1", label %"if_else.1"
while_end.1:
  %".136" = bitcast [18 x i8]* @"str_27" to i8*
  ret i8* %".136"
if_then.1:
  %"in_key_load" = load i64, i64* %"in_key"
  %"icmp.6" = icmp eq i64 %"in_key_load", 0
  br i1 %"icmp.6", label %"and_rhs", label %"and_end"
if_else.1:
  %"in_key_load.2" = load i64, i64* %"in_key"
  %"icmp.12" = icmp eq i64 %"in_key_load.2", 1
  br i1 %"icmp.12", label %"if_then.6", label %"if_else.6"
if_end.1:
  %"i_load.5" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.5", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond.1"
and_rhs:
  %"in_val_load" = load i64, i64* %"in_val"
  %"icmp.7" = icmp eq i64 %"in_val_load", 0
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"if_then.1"], [%"icmp.7", %"and_rhs"]
  br i1 %"and_result", label %"if_then.2", label %"if_else.2"
if_then.2:
  store i64 1, i64* %"in_key"
  %".39" = bitcast [1 x i8]* @"str_5" to i8*
  store i8* %".39", i8** %"current_key"
  br label %"if_end.2"
if_else.2:
  %"in_key_load.1" = load i64, i64* %"in_key"
  %"icmp.8" = icmp eq i64 %"in_key_load.1", 1
  br i1 %"icmp.8", label %"if_then.3", label %"if_else.3"
if_end.2:
  br label %"if_end.1"
if_then.3:
  store i64 0, i64* %"in_key"
  br label %"if_end.3"
if_else.3:
  %"in_val_load.1" = load i64, i64* %"in_val"
  %"icmp.9" = icmp eq i64 %"in_val_load.1", 0
  br i1 %"icmp.9", label %"if_then.4", label %"if_else.4"
if_end.3:
  br label %"if_end.2"
if_then.4:
  store i64 1, i64* %"in_val"
  %".47" = bitcast [1 x i8]* @"str_6" to i8*
  store i8* %".47", i8** %"current_val"
  store i64 0, i64* %"val_type"
  br label %"if_end.4"
if_else.4:
  %"in_val_load.2" = load i64, i64* %"in_val"
  %"icmp.10" = icmp eq i64 %"in_val_load.2", 1
  br i1 %"icmp.10", label %"and_rhs.1", label %"and_end.1"
if_end.4:
  br label %"if_end.3"
and_rhs.1:
  %"val_type_load" = load i64, i64* %"val_type"
  %"icmp.11" = icmp eq i64 %"val_type_load", 0
  br label %"and_end.1"
and_end.1:
  %"and_result.1" = phi  i1 [0, %"if_else.4"], [%"icmp.11", %"and_rhs.1"]
  br i1 %"and_result.1", label %"if_then.5", label %"if_else.5"
if_then.5:
  store i64 0, i64* %"in_val"
  %".55" = bitcast [7 x i8]* @"str_7" to i8*
  %".56" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".56", i8* %".55")
  %"current_key_load" = load i8*, i8** %"current_key"
  %".57" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".57")
  %".58" = bitcast [3 x i8]* @"str_10" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".58", i8* %"current_key_load")
  %".59" = bitcast [9 x i8]* @"str_11" to i8*
  %".60" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".60")
  %".61" = bitcast [3 x i8]* @"str_13" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".61", i8* %".59")
  %"current_val_load" = load i8*, i8** %"current_val"
  %".62" = bitcast [2 x i8]* @"str_14" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".62")
  %".63" = bitcast [3 x i8]* @"str_15" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".63", i8* %"current_val_load")
  %".64" = bitcast [2 x i8]* @"str_16" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".64")
  br label %"if_end.5"
if_else.5:
  br label %"if_end.5"
if_end.5:
  br label %"if_end.4"
if_then.6:
  %"current_key_load.1" = load i8*, i8** %"current_key"
  %"c_load.4" = load i64, i64* %"c.1"
  %"chr_trunc" = trunc i64 %"c_load.4" to i8
  %"chr_buf" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc", i8* %"chr_buf"
  %"chr_null_ptr" = getelementptr i8, i8* %"chr_buf", i64 1
  store i8 0, i8* %"chr_null_ptr"
  %"sconcat_len1" = call i64 @"strlen"(i8* %"current_key_load.1")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"chr_buf")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"current_key_load.1")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"chr_buf")
  store i8* %"sconcat_buf", i8** %"current_key"
  br label %"if_end.6"
if_else.6:
  %"in_val_load.3" = load i64, i64* %"in_val"
  %"icmp.13" = icmp eq i64 %"in_val_load.3", 1
  br i1 %"icmp.13", label %"and_rhs.2", label %"and_end.2"
if_end.6:
  br label %"if_end.1"
and_rhs.2:
  %"val_type_load.1" = load i64, i64* %"val_type"
  %"icmp.14" = icmp eq i64 %"val_type_load.1", 0
  br label %"and_end.2"
and_end.2:
  %"and_result.2" = phi  i1 [0, %"if_else.6"], [%"icmp.14", %"and_rhs.2"]
  br i1 %"and_result.2", label %"if_then.7", label %"if_else.7"
if_then.7:
  %"current_val_load.1" = load i8*, i8** %"current_val"
  %"c_load.5" = load i64, i64* %"c.1"
  %"chr_trunc.1" = trunc i64 %"c_load.5" to i8
  %"chr_buf.1" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc.1", i8* %"chr_buf.1"
  %"chr_null_ptr.1" = getelementptr i8, i8* %"chr_buf.1", i64 1
  store i8 0, i8* %"chr_null_ptr.1"
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"current_val_load.1")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %"chr_buf.1")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"current_val_load.1")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %"chr_buf.1")
  store i8* %"sconcat_buf.1", i8** %"current_val"
  br label %"if_end.7"
if_else.7:
  %"c_load.6" = load i64, i64* %"c.1"
  %"icmp.15" = icmp sge i64 %"c_load.6", 48
  br i1 %"icmp.15", label %"and_rhs.3", label %"and_end.3"
if_end.7:
  br label %"if_end.6"
and_rhs.3:
  %"c_load.7" = load i64, i64* %"c.1"
  %"icmp.16" = icmp sle i64 %"c_load.7", 57
  br label %"and_end.3"
and_end.3:
  %"and_result.3" = phi  i1 [0, %"if_else.7"], [%"icmp.16", %"and_rhs.3"]
  br i1 %"and_result.3", label %"and_rhs.4", label %"and_end.4"
and_rhs.4:
  %"in_val_load.4" = load i64, i64* %"in_val"
  %"icmp.17" = icmp eq i64 %"in_val_load.4", 0
  br label %"and_end.4"
and_end.4:
  %"and_result.4" = phi  i1 [0, %"and_end.3"], [%"icmp.17", %"and_rhs.4"]
  br i1 %"and_result.4", label %"and_rhs.5", label %"and_end.5"
and_rhs.5:
  %"in_key_load.3" = load i64, i64* %"in_key"
  %"icmp.18" = icmp eq i64 %"in_key_load.3", 0
  br label %"and_end.5"
and_end.5:
  %"and_result.5" = phi  i1 [0, %"and_end.4"], [%"icmp.18", %"and_rhs.5"]
  br i1 %"and_result.5", label %"if_then.8", label %"if_else.8"
if_then.8:
  store i64 1, i64* %"in_val"
  %"c_load.8" = load i64, i64* %"c.1"
  %"chr_trunc.2" = trunc i64 %"c_load.8" to i8
  %"chr_buf.2" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc.2", i8* %"chr_buf.2"
  %"chr_null_ptr.2" = getelementptr i8, i8* %"chr_buf.2", i64 1
  store i8 0, i8* %"chr_null_ptr.2"
  store i8* %"chr_buf.2", i8** %"current_val"
  store i64 1, i64* %"val_type"
  br label %"if_end.8"
if_else.8:
  %"in_val_load.5" = load i64, i64* %"in_val"
  %"icmp.19" = icmp eq i64 %"in_val_load.5", 1
  br i1 %"icmp.19", label %"and_rhs.6", label %"and_end.6"
if_end.8:
  br label %"if_end.7"
and_rhs.6:
  %"val_type_load.2" = load i64, i64* %"val_type"
  %"icmp.20" = icmp eq i64 %"val_type_load.2", 1
  br label %"and_end.6"
and_end.6:
  %"and_result.6" = phi  i1 [0, %"if_else.8"], [%"icmp.20", %"and_rhs.6"]
  br i1 %"and_result.6", label %"and_rhs.7", label %"and_end.7"
and_rhs.7:
  %"c_load.9" = load i64, i64* %"c.1"
  %"icmp.21" = icmp sge i64 %"c_load.9", 48
  br label %"and_end.7"
and_end.7:
  %"and_result.7" = phi  i1 [0, %"and_end.6"], [%"icmp.21", %"and_rhs.7"]
  br i1 %"and_result.7", label %"and_rhs.8", label %"and_end.8"
and_rhs.8:
  %"c_load.10" = load i64, i64* %"c.1"
  %"icmp.22" = icmp sle i64 %"c_load.10", 57
  br label %"and_end.8"
and_end.8:
  %"and_result.8" = phi  i1 [0, %"and_end.7"], [%"icmp.22", %"and_rhs.8"]
  br i1 %"and_result.8", label %"if_then.9", label %"if_else.9"
if_then.9:
  %"current_val_load.2" = load i8*, i8** %"current_val"
  %"c_load.11" = load i64, i64* %"c.1"
  %"chr_trunc.3" = trunc i64 %"c_load.11" to i8
  %"chr_buf.3" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc.3", i8* %"chr_buf.3"
  %"chr_null_ptr.3" = getelementptr i8, i8* %"chr_buf.3", i64 1
  store i8 0, i8* %"chr_null_ptr.3"
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"current_val_load.2")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %"chr_buf.3")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"current_val_load.2")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %"chr_buf.3")
  store i8* %"sconcat_buf.2", i8** %"current_val"
  br label %"if_end.9"
if_else.9:
  %"in_val_load.6" = load i64, i64* %"in_val"
  %"icmp.23" = icmp eq i64 %"in_val_load.6", 1
  br i1 %"icmp.23", label %"and_rhs.9", label %"and_end.9"
if_end.9:
  br label %"if_end.8"
and_rhs.9:
  %"val_type_load.3" = load i64, i64* %"val_type"
  %"icmp.24" = icmp eq i64 %"val_type_load.3", 1
  br label %"and_end.9"
and_end.9:
  %"and_result.9" = phi  i1 [0, %"if_else.9"], [%"icmp.24", %"and_rhs.9"]
  br i1 %"and_result.9", label %"and_rhs.10", label %"and_end.10"
and_rhs.10:
  %"c_load.12" = load i64, i64* %"c.1"
  %"icmp.25" = icmp eq i64 %"c_load.12", 32
  br i1 %"icmp.25", label %"or_end.2", label %"or_rhs.2"
and_end.10:
  %"and_result.10" = phi  i1 [0, %"and_end.9"], [%"or_result.3", %"or_end.3"]
  br i1 %"and_result.10", label %"if_then.10", label %"if_else.10"
or_rhs.2:
  %"c_load.13" = load i64, i64* %"c.1"
  %"icmp.26" = icmp eq i64 %"c_load.13", 44
  br label %"or_end.2"
or_end.2:
  %"or_result.2" = phi  i1 [1, %"and_rhs.10"], [%"icmp.26", %"or_rhs.2"]
  br i1 %"or_result.2", label %"or_end.3", label %"or_rhs.3"
or_rhs.3:
  %"c_load.14" = load i64, i64* %"c.1"
  %"icmp.27" = icmp eq i64 %"c_load.14", 125
  br label %"or_end.3"
or_end.3:
  %"or_result.3" = phi  i1 [1, %"or_end.2"], [%"icmp.27", %"or_rhs.3"]
  br label %"and_end.10"
if_then.10:
  store i64 0, i64* %"in_val"
  %".117" = bitcast [7 x i8]* @"str_17" to i8*
  %".118" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".118", i8* %".117")
  %"current_key_load.2" = load i8*, i8** %"current_key"
  %".119" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".119")
  %".120" = bitcast [3 x i8]* @"str_20" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".120", i8* %"current_key_load.2")
  %".121" = bitcast [9 x i8]* @"str_21" to i8*
  %".122" = bitcast [2 x i8]* @"str_22" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".122")
  %".123" = bitcast [3 x i8]* @"str_23" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".123", i8* %".121")
  %"current_val_load.3" = load i8*, i8** %"current_val"
  %".124" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_sep.5" = call i32 (i8*, ...) @"printf"(i8* %".124")
  %".125" = bitcast [3 x i8]* @"str_25" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".125", i8* %"current_val_load.3")
  %".126" = bitcast [2 x i8]* @"str_26" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".126")
  br label %"if_end.10"
if_else.10:
  br label %"if_end.10"
if_end.10:
  br label %"if_end.9"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"chr_trunc" = trunc i64 34 to i8
  %"chr_buf" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc", i8* %"chr_buf"
  %"chr_null_ptr" = getelementptr i8, i8* %"chr_buf", i64 1
  store i8 0, i8* %"chr_null_ptr"
  %"q" = alloca i8*
  store i8* %"chr_buf", i8** %"q"
  %".10" = bitcast [2 x i8]* @"str_28" to i8*
  %"q_load" = load i8*, i8** %"q"
  %"sconcat_len1" = call i64 @"strlen"(i8* %".10")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"q_load")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %".10")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"q_load")
  %".11" = bitcast [5 x i8]* @"str_29" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".11")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".11")
  %"q_load.1" = load i8*, i8** %"q"
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %"q_load.1")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %"q_load.1")
  %".12" = bitcast [2 x i8]* @"str_30" to i8*
  %"sconcat_len1.3" = call i64 @"strlen"(i8* %"sconcat_buf.2")
  %"sconcat_len2.3" = call i64 @"strlen"(i8* %".12")
  %"sconcat_sum.3" = add i64 %"sconcat_len1.3", %"sconcat_len2.3"
  %"sconcat_total.3" = add i64 %"sconcat_sum.3", 1
  %"sconcat_buf.3" = call i8* @"GC_malloc"(i64 %"sconcat_total.3")
  %"sconcat_cpy.3" = call i8* @"strcpy"(i8* %"sconcat_buf.3", i8* %"sconcat_buf.2")
  %"sconcat_cat.3" = call i8* @"strcat"(i8* %"sconcat_buf.3", i8* %".12")
  %"q_load.2" = load i8*, i8** %"q"
  %"sconcat_len1.4" = call i64 @"strlen"(i8* %"sconcat_buf.3")
  %"sconcat_len2.4" = call i64 @"strlen"(i8* %"q_load.2")
  %"sconcat_sum.4" = add i64 %"sconcat_len1.4", %"sconcat_len2.4"
  %"sconcat_total.4" = add i64 %"sconcat_sum.4", 1
  %"sconcat_buf.4" = call i8* @"GC_malloc"(i64 %"sconcat_total.4")
  %"sconcat_cpy.4" = call i8* @"strcpy"(i8* %"sconcat_buf.4", i8* %"sconcat_buf.3")
  %"sconcat_cat.4" = call i8* @"strcat"(i8* %"sconcat_buf.4", i8* %"q_load.2")
  %".13" = bitcast [7 x i8]* @"str_31" to i8*
  %"sconcat_len1.5" = call i64 @"strlen"(i8* %"sconcat_buf.4")
  %"sconcat_len2.5" = call i64 @"strlen"(i8* %".13")
  %"sconcat_sum.5" = add i64 %"sconcat_len1.5", %"sconcat_len2.5"
  %"sconcat_total.5" = add i64 %"sconcat_sum.5", 1
  %"sconcat_buf.5" = call i8* @"GC_malloc"(i64 %"sconcat_total.5")
  %"sconcat_cpy.5" = call i8* @"strcpy"(i8* %"sconcat_buf.5", i8* %"sconcat_buf.4")
  %"sconcat_cat.5" = call i8* @"strcat"(i8* %"sconcat_buf.5", i8* %".13")
  %"q_load.3" = load i8*, i8** %"q"
  %"sconcat_len1.6" = call i64 @"strlen"(i8* %"sconcat_buf.5")
  %"sconcat_len2.6" = call i64 @"strlen"(i8* %"q_load.3")
  %"sconcat_sum.6" = add i64 %"sconcat_len1.6", %"sconcat_len2.6"
  %"sconcat_total.6" = add i64 %"sconcat_sum.6", 1
  %"sconcat_buf.6" = call i8* @"GC_malloc"(i64 %"sconcat_total.6")
  %"sconcat_cpy.6" = call i8* @"strcpy"(i8* %"sconcat_buf.6", i8* %"sconcat_buf.5")
  %"sconcat_cat.6" = call i8* @"strcat"(i8* %"sconcat_buf.6", i8* %"q_load.3")
  %".14" = bitcast [2 x i8]* @"str_32" to i8*
  %"sconcat_len1.7" = call i64 @"strlen"(i8* %"sconcat_buf.6")
  %"sconcat_len2.7" = call i64 @"strlen"(i8* %".14")
  %"sconcat_sum.7" = add i64 %"sconcat_len1.7", %"sconcat_len2.7"
  %"sconcat_total.7" = add i64 %"sconcat_sum.7", 1
  %"sconcat_buf.7" = call i8* @"GC_malloc"(i64 %"sconcat_total.7")
  %"sconcat_cpy.7" = call i8* @"strcpy"(i8* %"sconcat_buf.7", i8* %"sconcat_buf.6")
  %"sconcat_cat.7" = call i8* @"strcat"(i8* %"sconcat_buf.7", i8* %".14")
  %"q_load.4" = load i8*, i8** %"q"
  %"sconcat_len1.8" = call i64 @"strlen"(i8* %"sconcat_buf.7")
  %"sconcat_len2.8" = call i64 @"strlen"(i8* %"q_load.4")
  %"sconcat_sum.8" = add i64 %"sconcat_len1.8", %"sconcat_len2.8"
  %"sconcat_total.8" = add i64 %"sconcat_sum.8", 1
  %"sconcat_buf.8" = call i8* @"GC_malloc"(i64 %"sconcat_total.8")
  %"sconcat_cpy.8" = call i8* @"strcpy"(i8* %"sconcat_buf.8", i8* %"sconcat_buf.7")
  %"sconcat_cat.8" = call i8* @"strcat"(i8* %"sconcat_buf.8", i8* %"q_load.4")
  %".15" = bitcast [7 x i8]* @"str_33" to i8*
  %"sconcat_len1.9" = call i64 @"strlen"(i8* %"sconcat_buf.8")
  %"sconcat_len2.9" = call i64 @"strlen"(i8* %".15")
  %"sconcat_sum.9" = add i64 %"sconcat_len1.9", %"sconcat_len2.9"
  %"sconcat_total.9" = add i64 %"sconcat_sum.9", 1
  %"sconcat_buf.9" = call i8* @"GC_malloc"(i64 %"sconcat_total.9")
  %"sconcat_cpy.9" = call i8* @"strcpy"(i8* %"sconcat_buf.9", i8* %"sconcat_buf.8")
  %"sconcat_cat.9" = call i8* @"strcat"(i8* %"sconcat_buf.9", i8* %".15")
  %"q_load.5" = load i8*, i8** %"q"
  %"sconcat_len1.10" = call i64 @"strlen"(i8* %"sconcat_buf.9")
  %"sconcat_len2.10" = call i64 @"strlen"(i8* %"q_load.5")
  %"sconcat_sum.10" = add i64 %"sconcat_len1.10", %"sconcat_len2.10"
  %"sconcat_total.10" = add i64 %"sconcat_sum.10", 1
  %"sconcat_buf.10" = call i8* @"GC_malloc"(i64 %"sconcat_total.10")
  %"sconcat_cpy.10" = call i8* @"strcpy"(i8* %"sconcat_buf.10", i8* %"sconcat_buf.9")
  %"sconcat_cat.10" = call i8* @"strcat"(i8* %"sconcat_buf.10", i8* %"q_load.5")
  %".16" = bitcast [4 x i8]* @"str_34" to i8*
  %"sconcat_len1.11" = call i64 @"strlen"(i8* %"sconcat_buf.10")
  %"sconcat_len2.11" = call i64 @"strlen"(i8* %".16")
  %"sconcat_sum.11" = add i64 %"sconcat_len1.11", %"sconcat_len2.11"
  %"sconcat_total.11" = add i64 %"sconcat_sum.11", 1
  %"sconcat_buf.11" = call i8* @"GC_malloc"(i64 %"sconcat_total.11")
  %"sconcat_cpy.11" = call i8* @"strcpy"(i8* %"sconcat_buf.11", i8* %"sconcat_buf.10")
  %"sconcat_cat.11" = call i8* @"strcat"(i8* %"sconcat_buf.11", i8* %".16")
  %"q_load.6" = load i8*, i8** %"q"
  %"sconcat_len1.12" = call i64 @"strlen"(i8* %"sconcat_buf.11")
  %"sconcat_len2.12" = call i64 @"strlen"(i8* %"q_load.6")
  %"sconcat_sum.12" = add i64 %"sconcat_len1.12", %"sconcat_len2.12"
  %"sconcat_total.12" = add i64 %"sconcat_sum.12", 1
  %"sconcat_buf.12" = call i8* @"GC_malloc"(i64 %"sconcat_total.12")
  %"sconcat_cpy.12" = call i8* @"strcpy"(i8* %"sconcat_buf.12", i8* %"sconcat_buf.11")
  %"sconcat_cat.12" = call i8* @"strcat"(i8* %"sconcat_buf.12", i8* %"q_load.6")
  %".17" = bitcast [6 x i8]* @"str_35" to i8*
  %"sconcat_len1.13" = call i64 @"strlen"(i8* %"sconcat_buf.12")
  %"sconcat_len2.13" = call i64 @"strlen"(i8* %".17")
  %"sconcat_sum.13" = add i64 %"sconcat_len1.13", %"sconcat_len2.13"
  %"sconcat_total.13" = add i64 %"sconcat_sum.13", 1
  %"sconcat_buf.13" = call i8* @"GC_malloc"(i64 %"sconcat_total.13")
  %"sconcat_cpy.13" = call i8* @"strcpy"(i8* %"sconcat_buf.13", i8* %"sconcat_buf.12")
  %"sconcat_cat.13" = call i8* @"strcat"(i8* %"sconcat_buf.13", i8* %".17")
  %"q_load.7" = load i8*, i8** %"q"
  %"sconcat_len1.14" = call i64 @"strlen"(i8* %"sconcat_buf.13")
  %"sconcat_len2.14" = call i64 @"strlen"(i8* %"q_load.7")
  %"sconcat_sum.14" = add i64 %"sconcat_len1.14", %"sconcat_len2.14"
  %"sconcat_total.14" = add i64 %"sconcat_sum.14", 1
  %"sconcat_buf.14" = call i8* @"GC_malloc"(i64 %"sconcat_total.14")
  %"sconcat_cpy.14" = call i8* @"strcpy"(i8* %"sconcat_buf.14", i8* %"sconcat_buf.13")
  %"sconcat_cat.14" = call i8* @"strcat"(i8* %"sconcat_buf.14", i8* %"q_load.7")
  %".18" = bitcast [7 x i8]* @"str_36" to i8*
  %"sconcat_len1.15" = call i64 @"strlen"(i8* %"sconcat_buf.14")
  %"sconcat_len2.15" = call i64 @"strlen"(i8* %".18")
  %"sconcat_sum.15" = add i64 %"sconcat_len1.15", %"sconcat_len2.15"
  %"sconcat_total.15" = add i64 %"sconcat_sum.15", 1
  %"sconcat_buf.15" = call i8* @"GC_malloc"(i64 %"sconcat_total.15")
  %"sconcat_cpy.15" = call i8* @"strcpy"(i8* %"sconcat_buf.15", i8* %"sconcat_buf.14")
  %"sconcat_cat.15" = call i8* @"strcat"(i8* %"sconcat_buf.15", i8* %".18")
  %"json" = alloca i8*
  store i8* %"sconcat_buf.15", i8** %"json"
  %"json_load" = load i8*, i8** %"json"
  %"parse_json_call" = call i8* @"parse_json"(i8* %"json_load")
  %"res" = alloca i8*
  store i8* %"parse_json_call", i8** %"res"
  %"res_load" = load i8*, i8** %"res"
  %".21" = bitcast [3 x i8]* @"str_37" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %"res_load")
  %".22" = bitcast [2 x i8]* @"str_38" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [1 x i8] c"\00"
@"str_1" = constant [1 x i8] c"\00"
@"str_2" = constant [30 x i8] c"--- Iniciando Parser JSON ---\00"
@"str_3" = constant [3 x i8] c"%s\00"
@"str_4" = constant [2 x i8] c"\0a\00"
@"str_5" = constant [1 x i8] c"\00"
@"str_6" = constant [1 x i8] c"\00"
@"str_7" = constant [7 x i8] c"Chave:\00"
@"str_8" = constant [3 x i8] c"%s\00"
@"str_9" = constant [2 x i8] c" \00"
@"str_10" = constant [3 x i8] c"%s\00"
@"str_11" = constant [9 x i8] c"| Valor:\00"
@"str_12" = constant [2 x i8] c" \00"
@"str_13" = constant [3 x i8] c"%s\00"
@"str_14" = constant [2 x i8] c" \00"
@"str_15" = constant [3 x i8] c"%s\00"
@"str_16" = constant [2 x i8] c"\0a\00"
@"str_17" = constant [7 x i8] c"Chave:\00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c" \00"
@"str_20" = constant [3 x i8] c"%s\00"
@"str_21" = constant [9 x i8] c"| Valor:\00"
@"str_22" = constant [2 x i8] c" \00"
@"str_23" = constant [3 x i8] c"%s\00"
@"str_24" = constant [2 x i8] c" \00"
@"str_25" = constant [3 x i8] c"%s\00"
@"str_26" = constant [2 x i8] c"\0a\00"
@"str_27" = constant [18 x i8] c"Parse conclu\c3\addo!\00"
@"str_28" = constant [2 x i8] c"{\00"
@"str_29" = constant [5 x i8] c"nome\00"
@"str_30" = constant [2 x i8] c":\00"
@"str_31" = constant [7 x i8] c"Lumina\00"
@"str_32" = constant [2 x i8] c",\00"
@"str_33" = constant [7 x i8] c"versao\00"
@"str_34" = constant [4 x i8] c":1,\00"
@"str_35" = constant [6 x i8] c"veloz\00"
@"str_36" = constant [7 x i8] c":true}\00"
@"str_37" = constant [3 x i8] c"%s\00"
@"str_38" = constant [2 x i8] c"\0a\00"