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
  %".7" = bitcast [36 x i8]* @"str_0" to i8*
  %".8" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %".10" = bitcast [21 x i8]* @"str_3" to i8*
  %"code" = alloca i8*
  store i8* %".10", i8** %"code"
  %"code_load" = load i8*, i8** %"code"
  %"len_str" = call i64 @"strlen"(i8* %"code_load")
  %"length" = alloca i64
  store i64 %"len_str", i64* %"length"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"length_load" = load i64, i64* %"length"
  %"icmp" = icmp slt i64 %"i_load", %"length_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"code_load.1" = load i8*, i8** %"code"
  %"i_load.1" = load i64, i64* %"i"
  %".16" = getelementptr i8, i8* %"code_load.1", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".16"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"c" = alloca i64
  store i64 %"idx_sext", i64* %"c"
  %"c_load" = load i64, i64* %"c"
  %"icmp.1" = icmp eq i64 %"c_load", 32
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %".110" = bitcast [41 x i8]* @"str_25" to i8*
  %".111" = bitcast [3 x i8]* @"str_26" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".111", i8* %".110")
  %".112" = bitcast [2 x i8]* @"str_27" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".112")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
if_then:
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
if_else:
  %"c_load.1" = load i64, i64* %"c"
  %"icmp.2" = icmp sge i64 %"c_load.1", 65
  br i1 %"icmp.2", label %"and_rhs", label %"and_end"
if_end:
  br label %"while_cond"
and_rhs:
  %"c_load.2" = load i64, i64* %"c"
  %"icmp.3" = icmp sle i64 %"c_load.2", 90
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"if_else"], [%"icmp.3", %"and_rhs"]
  br i1 %"and_result", label %"or_end", label %"or_rhs"
or_rhs:
  %"c_load.3" = load i64, i64* %"c"
  %"icmp.4" = icmp sge i64 %"c_load.3", 97
  br i1 %"icmp.4", label %"and_rhs.1", label %"and_end.1"
or_end:
  %"or_result" = phi  i1 [1, %"and_end"], [%"and_result.1", %"and_end.1"]
  br i1 %"or_result", label %"or_end.1", label %"or_rhs.1"
and_rhs.1:
  %"c_load.4" = load i64, i64* %"c"
  %"icmp.5" = icmp sle i64 %"c_load.4", 122
  br label %"and_end.1"
and_end.1:
  %"and_result.1" = phi  i1 [0, %"or_rhs"], [%"icmp.5", %"and_rhs.1"]
  br label %"or_end"
or_rhs.1:
  %"c_load.5" = load i64, i64* %"c"
  %"icmp.6" = icmp eq i64 %"c_load.5", 95
  br label %"or_end.1"
or_end.1:
  %"or_result.1" = phi  i1 [1, %"or_end"], [%"icmp.6", %"or_rhs.1"]
  br i1 %"or_result.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %".30" = bitcast [1 x i8]* @"str_4" to i8*
  %"word" = alloca i8*
  store i8* %".30", i8** %"word"
  br label %"while_cond.1"
if_else.1:
  %"c_load.6" = load i64, i64* %"c"
  %"icmp.15" = icmp sge i64 %"c_load.6", 48
  br i1 %"icmp.15", label %"and_rhs.5", label %"and_end.5"
if_end.1:
  br label %"if_end"
while_cond.1:
  %"i_load.3" = load i64, i64* %"i"
  %"length_load.1" = load i64, i64* %"length"
  %"icmp.7" = icmp slt i64 %"i_load.3", %"length_load.1"
  br i1 %"icmp.7", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"code_load.2" = load i8*, i8** %"code"
  %"i_load.4" = load i64, i64* %"i"
  %".34" = getelementptr i8, i8* %"code_load.2", i64 %"i_load.4"
  %"ptr_idx_load.1" = load i8, i8* %".34"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"ch" = alloca i64
  store i64 %"idx_sext.1", i64* %"ch"
  %"ch_load" = load i64, i64* %"ch"
  %"icmp.8" = icmp sge i64 %"ch_load", 65
  br i1 %"icmp.8", label %"and_rhs.2", label %"and_end.2"
while_end.1:
  %".56" = bitcast [7 x i8]* @"str_5" to i8*
  %".57" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".57", i8* %".56")
  %"word_load.1" = load i8*, i8** %"word"
  %".58" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".58")
  %".59" = bitcast [3 x i8]* @"str_8" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".59", i8* %"word_load.1")
  %".60" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".60")
  br label %"if_end.1"
and_rhs.2:
  %"ch_load.1" = load i64, i64* %"ch"
  %"icmp.9" = icmp sle i64 %"ch_load.1", 90
  br label %"and_end.2"
and_end.2:
  %"and_result.2" = phi  i1 [0, %"while_body.1"], [%"icmp.9", %"and_rhs.2"]
  br i1 %"and_result.2", label %"or_end.2", label %"or_rhs.2"
or_rhs.2:
  %"ch_load.2" = load i64, i64* %"ch"
  %"icmp.10" = icmp sge i64 %"ch_load.2", 97
  br i1 %"icmp.10", label %"and_rhs.3", label %"and_end.3"
or_end.2:
  %"or_result.2" = phi  i1 [1, %"and_end.2"], [%"and_result.3", %"and_end.3"]
  br i1 %"or_result.2", label %"or_end.3", label %"or_rhs.3"
and_rhs.3:
  %"ch_load.3" = load i64, i64* %"ch"
  %"icmp.11" = icmp sle i64 %"ch_load.3", 122
  br label %"and_end.3"
and_end.3:
  %"and_result.3" = phi  i1 [0, %"or_rhs.2"], [%"icmp.11", %"and_rhs.3"]
  br label %"or_end.2"
or_rhs.3:
  %"ch_load.4" = load i64, i64* %"ch"
  %"icmp.12" = icmp sge i64 %"ch_load.4", 48
  br i1 %"icmp.12", label %"and_rhs.4", label %"and_end.4"
or_end.3:
  %"or_result.3" = phi  i1 [1, %"or_end.2"], [%"and_result.4", %"and_end.4"]
  br i1 %"or_result.3", label %"or_end.4", label %"or_rhs.4"
and_rhs.4:
  %"ch_load.5" = load i64, i64* %"ch"
  %"icmp.13" = icmp sle i64 %"ch_load.5", 57
  br label %"and_end.4"
and_end.4:
  %"and_result.4" = phi  i1 [0, %"or_rhs.3"], [%"icmp.13", %"and_rhs.4"]
  br label %"or_end.3"
or_rhs.4:
  %"ch_load.6" = load i64, i64* %"ch"
  %"icmp.14" = icmp eq i64 %"ch_load.6", 95
  br label %"or_end.4"
or_end.4:
  %"or_result.4" = phi  i1 [1, %"or_end.3"], [%"icmp.14", %"or_rhs.4"]
  br i1 %"or_result.4", label %"if_then.2", label %"if_else.2"
if_then.2:
  %"word_load" = load i8*, i8** %"word"
  %"ch_load.7" = load i64, i64* %"ch"
  %"chr_trunc" = trunc i64 %"ch_load.7" to i8
  %"chr_buf" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc", i8* %"chr_buf"
  %"chr_null_ptr" = getelementptr i8, i8* %"chr_buf", i64 1
  store i8 0, i8* %"chr_null_ptr"
  %"sconcat_len1" = call i64 @"strlen"(i8* %"word_load")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"chr_buf")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"word_load")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"chr_buf")
  store i8* %"sconcat_buf", i8** %"word"
  %"i_load.5" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.5", 1
  store i64 %"add.1", i64* %"i"
  br label %"if_end.2"
if_else.2:
  br label %"while_end.1"
if_end.2:
  br label %"while_cond.1"
and_rhs.5:
  %"c_load.7" = load i64, i64* %"c"
  %"icmp.16" = icmp sle i64 %"c_load.7", 57
  br label %"and_end.5"
and_end.5:
  %"and_result.5" = phi  i1 [0, %"if_else.1"], [%"icmp.16", %"and_rhs.5"]
  br i1 %"and_result.5", label %"if_then.3", label %"if_else.3"
if_then.3:
  %".65" = bitcast [1 x i8]* @"str_10" to i8*
  %"num" = alloca i8*
  store i8* %".65", i8** %"num"
  br label %"while_cond.2"
if_else.3:
  %"c_load.8" = load i64, i64* %"c"
  %"icmp.20" = icmp eq i64 %"c_load.8", 40
  br i1 %"icmp.20", label %"if_then.5", label %"if_else.5"
if_end.3:
  br label %"if_end.1"
while_cond.2:
  %"i_load.6" = load i64, i64* %"i"
  %"length_load.2" = load i64, i64* %"length"
  %"icmp.17" = icmp slt i64 %"i_load.6", %"length_load.2"
  br i1 %"icmp.17", label %"while_body.2", label %"while_end.2"
while_body.2:
  %"code_load.3" = load i8*, i8** %"code"
  %"i_load.7" = load i64, i64* %"i"
  %".69" = getelementptr i8, i8* %"code_load.3", i64 %"i_load.7"
  %"ptr_idx_load.2" = load i8, i8* %".69"
  %"idx_sext.2" = sext i8 %"ptr_idx_load.2" to i64
  %"nch" = alloca i64
  store i64 %"idx_sext.2", i64* %"nch"
  %"nch_load" = load i64, i64* %"nch"
  %"icmp.18" = icmp sge i64 %"nch_load", 48
  br i1 %"icmp.18", label %"and_rhs.6", label %"and_end.6"
while_end.2:
  %".81" = bitcast [8 x i8]* @"str_11" to i8*
  %".82" = bitcast [3 x i8]* @"str_12" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".82", i8* %".81")
  %"num_load.1" = load i8*, i8** %"num"
  %".83" = bitcast [2 x i8]* @"str_13" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".83")
  %".84" = bitcast [3 x i8]* @"str_14" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".84", i8* %"num_load.1")
  %".85" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".85")
  br label %"if_end.3"
and_rhs.6:
  %"nch_load.1" = load i64, i64* %"nch"
  %"icmp.19" = icmp sle i64 %"nch_load.1", 57
  br label %"and_end.6"
and_end.6:
  %"and_result.6" = phi  i1 [0, %"while_body.2"], [%"icmp.19", %"and_rhs.6"]
  br i1 %"and_result.6", label %"if_then.4", label %"if_else.4"
if_then.4:
  %"num_load" = load i8*, i8** %"num"
  %"nch_load.2" = load i64, i64* %"nch"
  %"chr_trunc.1" = trunc i64 %"nch_load.2" to i8
  %"chr_buf.1" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc.1", i8* %"chr_buf.1"
  %"chr_null_ptr.1" = getelementptr i8, i8* %"chr_buf.1", i64 1
  store i8 0, i8* %"chr_null_ptr.1"
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"num_load")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %"chr_buf.1")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"num_load")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %"chr_buf.1")
  store i8* %"sconcat_buf.1", i8** %"num"
  %"i_load.8" = load i64, i64* %"i"
  %"add.2" = add i64 %"i_load.8", 1
  store i64 %"add.2", i64* %"i"
  br label %"if_end.4"
if_else.4:
  br label %"while_end.2"
if_end.4:
  br label %"while_cond.2"
if_then.5:
  %".88" = bitcast [6 x i8]* @"str_16" to i8*
  %".89" = bitcast [3 x i8]* @"str_17" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".89", i8* %".88")
  %".90" = bitcast [2 x i8]* @"str_18" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".90")
  br label %"if_end.5"
if_else.5:
  %"c_load.9" = load i64, i64* %"c"
  %"icmp.21" = icmp eq i64 %"c_load.9", 41
  br i1 %"icmp.21", label %"if_then.6", label %"if_else.6"
if_end.5:
  %"i_load.9" = load i64, i64* %"i"
  %"add.3" = add i64 %"i_load.9", 1
  store i64 %"add.3", i64* %"i"
  br label %"if_end.3"
if_then.6:
  %".93" = bitcast [6 x i8]* @"str_19" to i8*
  %".94" = bitcast [3 x i8]* @"str_20" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".94", i8* %".93")
  %".95" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".95")
  br label %"if_end.6"
if_else.6:
  %"c_load.10" = load i64, i64* %"c"
  %"icmp.22" = icmp eq i64 %"c_load.10", 58
  br i1 %"icmp.22", label %"if_then.7", label %"if_else.7"
if_end.6:
  br label %"if_end.5"
if_then.7:
  %".98" = bitcast [6 x i8]* @"str_22" to i8*
  %".99" = bitcast [3 x i8]* @"str_23" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".99", i8* %".98")
  %".100" = bitcast [2 x i8]* @"str_24" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".100")
  br label %"if_end.7"
if_else.7:
  br label %"if_end.7"
if_end.7:
  br label %"if_end.6"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [36 x i8] c"Iniciando Lexer nativo da Lumina...\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [21 x i8] c"fn main(): print(42)\00"
@"str_4" = constant [1 x i8] c"\00"
@"str_5" = constant [7 x i8] c"IDENT:\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [3 x i8] c"%s\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [1 x i8] c"\00"
@"str_11" = constant [8 x i8] c"NUMBER:\00"
@"str_12" = constant [3 x i8] c"%s\00"
@"str_13" = constant [2 x i8] c" \00"
@"str_14" = constant [3 x i8] c"%s\00"
@"str_15" = constant [2 x i8] c"\0a\00"
@"str_16" = constant [6 x i8] c"OP: (\00"
@"str_17" = constant [3 x i8] c"%s\00"
@"str_18" = constant [2 x i8] c"\0a\00"
@"str_19" = constant [6 x i8] c"OP: )\00"
@"str_20" = constant [3 x i8] c"%s\00"
@"str_21" = constant [2 x i8] c"\0a\00"
@"str_22" = constant [6 x i8] c"OP: :\00"
@"str_23" = constant [3 x i8] c"%s\00"
@"str_24" = constant [2 x i8] c"\0a\00"
@"str_25" = constant [41 x i8] c"An\c3\a1lise L\c3\a9xica conclu\c3\adda com sucesso!\00"
@"str_26" = constant [3 x i8] c"%s\00"
@"str_27" = constant [2 x i8] c"\0a\00"