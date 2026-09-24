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
  %".7" = bitcast [10 x i8]* @"str_0" to i8*
  %"code" = alloca i8*
  store i8* %".7", i8** %"code"
  %"code_load" = load i8*, i8** %"code"
  %"len_str" = call i64 @"strlen"(i8* %"code_load")
  %"length" = alloca i64
  store i64 %"len_str", i64* %"length"
  %"array_lit" = alloca [15 x i64]
  %"arr_el_0" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 0
  store i64 0, i64* %"arr_el_0"
  %"arr_el_1" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 1
  store i64 0, i64* %"arr_el_1"
  %"arr_el_2" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 2
  store i64 0, i64* %"arr_el_2"
  %"arr_el_3" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 3
  store i64 0, i64* %"arr_el_3"
  %"arr_el_4" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 4
  store i64 0, i64* %"arr_el_4"
  %"arr_el_5" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 5
  store i64 0, i64* %"arr_el_5"
  %"arr_el_6" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 6
  store i64 0, i64* %"arr_el_6"
  %"arr_el_7" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 7
  store i64 0, i64* %"arr_el_7"
  %"arr_el_8" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 8
  store i64 0, i64* %"arr_el_8"
  %"arr_el_9" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 9
  store i64 0, i64* %"arr_el_9"
  %"arr_el_10" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 10
  store i64 0, i64* %"arr_el_10"
  %"arr_el_11" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 11
  store i64 0, i64* %"arr_el_11"
  %"arr_el_12" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 12
  store i64 0, i64* %"arr_el_12"
  %"arr_el_13" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 13
  store i64 0, i64* %"arr_el_13"
  %"arr_el_14" = getelementptr [15 x i64], [15 x i64]* %"array_lit", i32 0, i32 14
  store i64 0, i64* %"arr_el_14"
  %"tokens" = alloca i64*
  %"ptr_cast" = bitcast [15 x i64]* %"array_lit" to i64*
  store i64* %"ptr_cast", i64** %"tokens"
  %"token_count" = alloca i64
  store i64 0, i64* %"token_count"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  %"current_num" = alloca i64
  store i64 0, i64* %"current_num"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"length_load" = load i64, i64* %"length"
  %"icmp" = icmp slt i64 %"i_load", %"length_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"code_load.1" = load i8*, i8** %"code"
  %"i_load.1" = load i64, i64* %"i"
  %".31" = getelementptr i8, i8* %"code_load.1", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".31"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"c" = alloca i64
  store i64 %"idx_sext", i64* %"c"
  %"c_load" = load i64, i64* %"c"
  %"icmp.1" = icmp sge i64 %"c_load", 48
  br i1 %"icmp.1", label %"and_rhs", label %"and_end"
while_end:
  %"current_num_load.3" = load i64, i64* %"current_num"
  %"icmp.8" = icmp sgt i64 %"current_num_load.3", 0
  br i1 %"icmp.8", label %"if_then.6", label %"if_else.6"
and_rhs:
  %"c_load.1" = load i64, i64* %"c"
  %"icmp.2" = icmp sle i64 %"c_load.1", 57
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_body"], [%"icmp.2", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  %"current_num_load" = load i64, i64* %"current_num"
  %"mul" = mul i64 %"current_num_load", 10
  %"c_load.2" = load i64, i64* %"c"
  %"sub" = sub i64 %"c_load.2", 48
  %"add" = add i64 %"mul", %"sub"
  store i64 %"add", i64* %"current_num"
  br label %"if_end"
if_else:
  %"current_num_load.1" = load i64, i64* %"current_num"
  %"icmp.3" = icmp sgt i64 %"current_num_load.1", 0
  br i1 %"icmp.3", label %"if_then.1", label %"if_else.1"
if_end:
  %"i_load.2" = load i64, i64* %"i"
  %"add.7" = add i64 %"i_load.2", 1
  store i64 %"add.7", i64* %"i"
  br label %"while_cond"
if_then.1:
  %"current_num_load.2" = load i64, i64* %"current_num"
  %"add.1" = add i64 %"current_num_load.2", 1000
  %"tokens_load" = load i64*, i64** %"tokens"
  %"token_count_load" = load i64, i64* %"token_count"
  %"idx_ptr" = getelementptr i64, i64* %"tokens_load", i64 %"token_count_load"
  store i64 %"add.1", i64* %"idx_ptr"
  %"token_count_load.1" = load i64, i64* %"token_count"
  %"add.2" = add i64 %"token_count_load.1", 1
  store i64 %"add.2", i64* %"token_count"
  store i64 0, i64* %"current_num"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"c_load.3" = load i64, i64* %"c"
  %"icmp.4" = icmp eq i64 %"c_load.3", 43
  br i1 %"icmp.4", label %"if_then.2", label %"if_else.2"
if_then.2:
  %"tokens_load.1" = load i64*, i64** %"tokens"
  %"token_count_load.2" = load i64, i64* %"token_count"
  %"idx_ptr.1" = getelementptr i64, i64* %"tokens_load.1", i64 %"token_count_load.2"
  store i64 1, i64* %"idx_ptr.1"
  %"token_count_load.3" = load i64, i64* %"token_count"
  %"add.3" = add i64 %"token_count_load.3", 1
  store i64 %"add.3", i64* %"token_count"
  br label %"if_end.2"
if_else.2:
  %"c_load.4" = load i64, i64* %"c"
  %"icmp.5" = icmp eq i64 %"c_load.4", 45
  br i1 %"icmp.5", label %"if_then.3", label %"if_else.3"
if_end.2:
  br label %"if_end"
if_then.3:
  %"tokens_load.2" = load i64*, i64** %"tokens"
  %"token_count_load.4" = load i64, i64* %"token_count"
  %"idx_ptr.2" = getelementptr i64, i64* %"tokens_load.2", i64 %"token_count_load.4"
  store i64 2, i64* %"idx_ptr.2"
  %"token_count_load.5" = load i64, i64* %"token_count"
  %"add.4" = add i64 %"token_count_load.5", 1
  store i64 %"add.4", i64* %"token_count"
  br label %"if_end.3"
if_else.3:
  %"c_load.5" = load i64, i64* %"c"
  %"icmp.6" = icmp eq i64 %"c_load.5", 42
  br i1 %"icmp.6", label %"if_then.4", label %"if_else.4"
if_end.3:
  br label %"if_end.2"
if_then.4:
  %"tokens_load.3" = load i64*, i64** %"tokens"
  %"token_count_load.6" = load i64, i64* %"token_count"
  %"idx_ptr.3" = getelementptr i64, i64* %"tokens_load.3", i64 %"token_count_load.6"
  store i64 3, i64* %"idx_ptr.3"
  %"token_count_load.7" = load i64, i64* %"token_count"
  %"add.5" = add i64 %"token_count_load.7", 1
  store i64 %"add.5", i64* %"token_count"
  br label %"if_end.4"
if_else.4:
  %"c_load.6" = load i64, i64* %"c"
  %"icmp.7" = icmp eq i64 %"c_load.6", 47
  br i1 %"icmp.7", label %"if_then.5", label %"if_else.5"
if_end.4:
  br label %"if_end.3"
if_then.5:
  %"tokens_load.4" = load i64*, i64** %"tokens"
  %"token_count_load.8" = load i64, i64* %"token_count"
  %"idx_ptr.4" = getelementptr i64, i64* %"tokens_load.4", i64 %"token_count_load.8"
  store i64 4, i64* %"idx_ptr.4"
  %"token_count_load.9" = load i64, i64* %"token_count"
  %"add.6" = add i64 %"token_count_load.9", 1
  store i64 %"add.6", i64* %"token_count"
  br label %"if_end.5"
if_else.5:
  br label %"if_end.5"
if_end.5:
  br label %"if_end.4"
if_then.6:
  %"current_num_load.4" = load i64, i64* %"current_num"
  %"add.8" = add i64 %"current_num_load.4", 1000
  %"tokens_load.5" = load i64*, i64** %"tokens"
  %"token_count_load.10" = load i64, i64* %"token_count"
  %"idx_ptr.5" = getelementptr i64, i64* %"tokens_load.5", i64 %"token_count_load.10"
  store i64 %"add.8", i64* %"idx_ptr.5"
  %"token_count_load.11" = load i64, i64* %"token_count"
  %"add.9" = add i64 %"token_count_load.11", 1
  store i64 %"add.9", i64* %"token_count"
  br label %"if_end.6"
if_else.6:
  br label %"if_end.6"
if_end.6:
  %"array_lit.1" = alloca [10 x i64]
  %"arr_el_0.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 0
  store i64 0, i64* %"arr_el_0.1"
  %"arr_el_1.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 1
  store i64 0, i64* %"arr_el_1.1"
  %"arr_el_2.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 2
  store i64 0, i64* %"arr_el_2.1"
  %"arr_el_3.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 3
  store i64 0, i64* %"arr_el_3.1"
  %"arr_el_4.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 4
  store i64 0, i64* %"arr_el_4.1"
  %"arr_el_5.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 5
  store i64 0, i64* %"arr_el_5.1"
  %"arr_el_6.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 6
  store i64 0, i64* %"arr_el_6.1"
  %"arr_el_7.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 7
  store i64 0, i64* %"arr_el_7.1"
  %"arr_el_8.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 8
  store i64 0, i64* %"arr_el_8.1"
  %"arr_el_9.1" = getelementptr [10 x i64], [10 x i64]* %"array_lit.1", i32 0, i32 9
  store i64 0, i64* %"arr_el_9.1"
  %"values" = alloca i64*
  %"ptr_cast.1" = bitcast [10 x i64]* %"array_lit.1" to i64*
  store i64* %"ptr_cast.1", i64** %"values"
  %"val_count" = alloca i64
  store i64 0, i64* %"val_count"
  %"array_lit.2" = alloca [10 x i64]
  %"arr_el_0.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 0
  store i64 0, i64* %"arr_el_0.2"
  %"arr_el_1.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 1
  store i64 0, i64* %"arr_el_1.2"
  %"arr_el_2.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 2
  store i64 0, i64* %"arr_el_2.2"
  %"arr_el_3.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 3
  store i64 0, i64* %"arr_el_3.2"
  %"arr_el_4.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 4
  store i64 0, i64* %"arr_el_4.2"
  %"arr_el_5.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 5
  store i64 0, i64* %"arr_el_5.2"
  %"arr_el_6.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 6
  store i64 0, i64* %"arr_el_6.2"
  %"arr_el_7.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 7
  store i64 0, i64* %"arr_el_7.2"
  %"arr_el_8.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 8
  store i64 0, i64* %"arr_el_8.2"
  %"arr_el_9.2" = getelementptr [10 x i64], [10 x i64]* %"array_lit.2", i32 0, i32 9
  store i64 0, i64* %"arr_el_9.2"
  %"ops" = alloca i64*
  %"ptr_cast.2" = bitcast [10 x i64]* %"array_lit.2" to i64*
  store i64* %"ptr_cast.2", i64** %"ops"
  %"op_count" = alloca i64
  store i64 0, i64* %"op_count"
  %"j" = alloca i64
  store i64 0, i64* %"j"
  br label %"while_cond.1"
while_cond.1:
  %"j_load" = load i64, i64* %"j"
  %"token_count_load.12" = load i64, i64* %"token_count"
  %"icmp.9" = icmp slt i64 %"j_load", %"token_count_load.12"
  br i1 %"icmp.9", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"tokens_load.6" = load i64*, i64** %"tokens"
  %"j_load.1" = load i64, i64* %"j"
  %".99" = getelementptr i64, i64* %"tokens_load.6", i64 %"j_load.1"
  %"ptr_idx_load.1" = load i64, i64* %".99"
  %"t" = alloca i64
  store i64 %"ptr_idx_load.1", i64* %"t"
  %"t_load" = load i64, i64* %"t"
  %"icmp.10" = icmp sgt i64 %"t_load", 1000
  br i1 %"icmp.10", label %"if_then.7", label %"if_else.7"
while_end.1:
  br label %"while_cond.3"
if_then.7:
  %"t_load.1" = load i64, i64* %"t"
  %"sub.1" = sub i64 %"t_load.1", 1000
  %"values_load" = load i64*, i64** %"values"
  %"val_count_load" = load i64, i64* %"val_count"
  %"idx_ptr.6" = getelementptr i64, i64* %"values_load", i64 %"val_count_load"
  store i64 %"sub.1", i64* %"idx_ptr.6"
  %"val_count_load.1" = load i64, i64* %"val_count"
  %"add.10" = add i64 %"val_count_load.1", 1
  store i64 %"add.10", i64* %"val_count"
  br label %"if_end.7"
if_else.7:
  %"keep_popping" = alloca i1
  store i1 1, i1* %"keep_popping"
  br label %"while_cond.2"
if_end.7:
  %"j_load.2" = load i64, i64* %"j"
  %"add.14" = add i64 %"j_load.2", 1
  store i64 %"add.14", i64* %"j"
  br label %"while_cond.1"
while_cond.2:
  %"op_count_load" = load i64, i64* %"op_count"
  %"icmp.11" = icmp sgt i64 %"op_count_load", 0
  br i1 %"icmp.11", label %"and_rhs.1", label %"and_end.1"
while_body.2:
  %"ops_load" = load i64*, i64** %"ops"
  %"op_count_load.1" = load i64, i64* %"op_count"
  %"sub.2" = sub i64 %"op_count_load.1", 1
  %".110" = getelementptr i64, i64* %"ops_load", i64 %"sub.2"
  %"ptr_idx_load.2" = load i64, i64* %".110"
  %"top_op" = alloca i64
  store i64 %"ptr_idx_load.2", i64* %"top_op"
  %"t_load.2" = load i64, i64* %"t"
  %"icmp.13" = icmp sle i64 %"t_load.2", 2
  br i1 %"icmp.13", label %"or_end", label %"or_rhs"
while_end.2:
  %"t_load.3" = load i64, i64* %"t"
  %"ops_load.1" = load i64*, i64** %"ops"
  %"op_count_load.3" = load i64, i64* %"op_count"
  %"idx_ptr.11" = getelementptr i64, i64* %"ops_load.1", i64 %"op_count_load.3"
  store i64 %"t_load.3", i64* %"idx_ptr.11"
  %"op_count_load.4" = load i64, i64* %"op_count"
  %"add.13" = add i64 %"op_count_load.4", 1
  store i64 %"add.13", i64* %"op_count"
  br label %"if_end.7"
and_rhs.1:
  %"keep_popping_load" = load i1, i1* %"keep_popping"
  %"icmp.12" = icmp eq i1 %"keep_popping_load", 1
  br label %"and_end.1"
and_end.1:
  %"and_result.1" = phi  i1 [0, %"while_cond.2"], [%"icmp.12", %"and_rhs.1"]
  br i1 %"and_result.1", label %"while_body.2", label %"while_end.2"
or_rhs:
  %"top_op_load" = load i64, i64* %"top_op"
  %"icmp.14" = icmp sge i64 %"top_op_load", 3
  br label %"or_end"
or_end:
  %"or_result" = phi  i1 [1, %"while_body.2"], [%"icmp.14", %"or_rhs"]
  br i1 %"or_result", label %"if_then.8", label %"if_else.8"
if_then.8:
  %"values_load.1" = load i64*, i64** %"values"
  %"val_count_load.2" = load i64, i64* %"val_count"
  %"sub.3" = sub i64 %"val_count_load.2", 1
  %".115" = getelementptr i64, i64* %"values_load.1", i64 %"sub.3"
  %"ptr_idx_load.3" = load i64, i64* %".115"
  %"right" = alloca i64
  store i64 %"ptr_idx_load.3", i64* %"right"
  %"val_count_load.3" = load i64, i64* %"val_count"
  %"sub.4" = sub i64 %"val_count_load.3", 1
  store i64 %"sub.4", i64* %"val_count"
  %"values_load.2" = load i64*, i64** %"values"
  %"val_count_load.4" = load i64, i64* %"val_count"
  %"sub.5" = sub i64 %"val_count_load.4", 1
  %".118" = getelementptr i64, i64* %"values_load.2", i64 %"sub.5"
  %"ptr_idx_load.4" = load i64, i64* %".118"
  %"left" = alloca i64
  store i64 %"ptr_idx_load.4", i64* %"left"
  %"val_count_load.5" = load i64, i64* %"val_count"
  %"sub.6" = sub i64 %"val_count_load.5", 1
  store i64 %"sub.6", i64* %"val_count"
  %"top_op_load.1" = load i64, i64* %"top_op"
  %"icmp.15" = icmp eq i64 %"top_op_load.1", 1
  br i1 %"icmp.15", label %"if_then.9", label %"if_else.9"
if_else.8:
  store i1 0, i1* %"keep_popping"
  br label %"if_end.8"
if_end.8:
  br label %"while_cond.2"
if_then.9:
  %"left_load" = load i64, i64* %"left"
  %"right_load" = load i64, i64* %"right"
  %"add.11" = add i64 %"left_load", %"right_load"
  %"values_load.3" = load i64*, i64** %"values"
  %"val_count_load.6" = load i64, i64* %"val_count"
  %"idx_ptr.7" = getelementptr i64, i64* %"values_load.3", i64 %"val_count_load.6"
  store i64 %"add.11", i64* %"idx_ptr.7"
  br label %"if_end.9"
if_else.9:
  %"top_op_load.2" = load i64, i64* %"top_op"
  %"icmp.16" = icmp eq i64 %"top_op_load.2", 2
  br i1 %"icmp.16", label %"if_then.10", label %"if_else.10"
if_end.9:
  %"val_count_load.10" = load i64, i64* %"val_count"
  %"add.12" = add i64 %"val_count_load.10", 1
  store i64 %"add.12", i64* %"val_count"
  %"op_count_load.2" = load i64, i64* %"op_count"
  %"sub.8" = sub i64 %"op_count_load.2", 1
  store i64 %"sub.8", i64* %"op_count"
  br label %"if_end.8"
if_then.10:
  %"left_load.1" = load i64, i64* %"left"
  %"right_load.1" = load i64, i64* %"right"
  %"sub.7" = sub i64 %"left_load.1", %"right_load.1"
  %"values_load.4" = load i64*, i64** %"values"
  %"val_count_load.7" = load i64, i64* %"val_count"
  %"idx_ptr.8" = getelementptr i64, i64* %"values_load.4", i64 %"val_count_load.7"
  store i64 %"sub.7", i64* %"idx_ptr.8"
  br label %"if_end.10"
if_else.10:
  %"top_op_load.3" = load i64, i64* %"top_op"
  %"icmp.17" = icmp eq i64 %"top_op_load.3", 3
  br i1 %"icmp.17", label %"if_then.11", label %"if_else.11"
if_end.10:
  br label %"if_end.9"
if_then.11:
  %"left_load.2" = load i64, i64* %"left"
  %"right_load.2" = load i64, i64* %"right"
  %"mul.1" = mul i64 %"left_load.2", %"right_load.2"
  %"values_load.5" = load i64*, i64** %"values"
  %"val_count_load.8" = load i64, i64* %"val_count"
  %"idx_ptr.9" = getelementptr i64, i64* %"values_load.5", i64 %"val_count_load.8"
  store i64 %"mul.1", i64* %"idx_ptr.9"
  br label %"if_end.11"
if_else.11:
  %"top_op_load.4" = load i64, i64* %"top_op"
  %"icmp.18" = icmp eq i64 %"top_op_load.4", 4
  br i1 %"icmp.18", label %"if_then.12", label %"if_else.12"
if_end.11:
  br label %"if_end.10"
if_then.12:
  %"left_load.3" = load i64, i64* %"left"
  %"right_load.3" = load i64, i64* %"right"
  %"div" = sdiv i64 %"left_load.3", %"right_load.3"
  %"values_load.6" = load i64*, i64** %"values"
  %"val_count_load.9" = load i64, i64* %"val_count"
  %"idx_ptr.10" = getelementptr i64, i64* %"values_load.6", i64 %"val_count_load.9"
  store i64 %"div", i64* %"idx_ptr.10"
  br label %"if_end.12"
if_else.12:
  br label %"if_end.12"
if_end.12:
  br label %"if_end.11"
while_cond.3:
  %"op_count_load.5" = load i64, i64* %"op_count"
  %"icmp.19" = icmp sgt i64 %"op_count_load.5", 0
  br i1 %"icmp.19", label %"while_body.3", label %"while_end.3"
while_body.3:
  %"ops_load.2" = load i64*, i64** %"ops"
  %"op_count_load.6" = load i64, i64* %"op_count"
  %"sub.9" = sub i64 %"op_count_load.6", 1
  %".150" = getelementptr i64, i64* %"ops_load.2", i64 %"sub.9"
  %"ptr_idx_load.5" = load i64, i64* %".150"
  %"top_op.1" = alloca i64
  store i64 %"ptr_idx_load.5", i64* %"top_op.1"
  %"values_load.7" = load i64*, i64** %"values"
  %"val_count_load.11" = load i64, i64* %"val_count"
  %"sub.10" = sub i64 %"val_count_load.11", 1
  %".152" = getelementptr i64, i64* %"values_load.7", i64 %"sub.10"
  %"ptr_idx_load.6" = load i64, i64* %".152"
  %"right.1" = alloca i64
  store i64 %"ptr_idx_load.6", i64* %"right.1"
  %"val_count_load.12" = load i64, i64* %"val_count"
  %"sub.11" = sub i64 %"val_count_load.12", 1
  store i64 %"sub.11", i64* %"val_count"
  %"values_load.8" = load i64*, i64** %"values"
  %"val_count_load.13" = load i64, i64* %"val_count"
  %"sub.12" = sub i64 %"val_count_load.13", 1
  %".155" = getelementptr i64, i64* %"values_load.8", i64 %"sub.12"
  %"ptr_idx_load.7" = load i64, i64* %".155"
  %"left.1" = alloca i64
  store i64 %"ptr_idx_load.7", i64* %"left.1"
  %"val_count_load.14" = load i64, i64* %"val_count"
  %"sub.13" = sub i64 %"val_count_load.14", 1
  store i64 %"sub.13", i64* %"val_count"
  %"top_op_load.5" = load i64, i64* %"top_op.1"
  %"icmp.20" = icmp eq i64 %"top_op_load.5", 1
  br i1 %"icmp.20", label %"if_then.13", label %"if_else.13"
while_end.3:
  %".177" = bitcast [15 x i8]* @"str_1" to i8*
  %".178" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".178", i8* %".177")
  %"code_load.2" = load i8*, i8** %"code"
  %".179" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".179")
  %".180" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".180", i8* %"code_load.2")
  %".181" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".181")
  %".182" = bitcast [26 x i8]* @"str_6" to i8*
  %".183" = bitcast [3 x i8]* @"str_7" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".183", i8* %".182")
  %"values_load.13" = load i64*, i64** %"values"
  %".184" = getelementptr i64, i64* %"values_load.13", i64 0
  %"ptr_idx_load.8" = load i64, i64* %".184"
  %".185" = bitcast [2 x i8]* @"str_8" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".185")
  %".186" = bitcast [4 x i8]* @"str_9" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".186", i64 %"ptr_idx_load.8")
  %".187" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".187")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
if_then.13:
  %"left_load.4" = load i64, i64* %"left.1"
  %"right_load.4" = load i64, i64* %"right.1"
  %"add.15" = add i64 %"left_load.4", %"right_load.4"
  %"values_load.9" = load i64*, i64** %"values"
  %"val_count_load.15" = load i64, i64* %"val_count"
  %"idx_ptr.12" = getelementptr i64, i64* %"values_load.9", i64 %"val_count_load.15"
  store i64 %"add.15", i64* %"idx_ptr.12"
  br label %"if_end.13"
if_else.13:
  %"top_op_load.6" = load i64, i64* %"top_op.1"
  %"icmp.21" = icmp eq i64 %"top_op_load.6", 2
  br i1 %"icmp.21", label %"if_then.14", label %"if_else.14"
if_end.13:
  %"val_count_load.19" = load i64, i64* %"val_count"
  %"add.16" = add i64 %"val_count_load.19", 1
  store i64 %"add.16", i64* %"val_count"
  %"op_count_load.7" = load i64, i64* %"op_count"
  %"sub.15" = sub i64 %"op_count_load.7", 1
  store i64 %"sub.15", i64* %"op_count"
  br label %"while_cond.3"
if_then.14:
  %"left_load.5" = load i64, i64* %"left.1"
  %"right_load.5" = load i64, i64* %"right.1"
  %"sub.14" = sub i64 %"left_load.5", %"right_load.5"
  %"values_load.10" = load i64*, i64** %"values"
  %"val_count_load.16" = load i64, i64* %"val_count"
  %"idx_ptr.13" = getelementptr i64, i64* %"values_load.10", i64 %"val_count_load.16"
  store i64 %"sub.14", i64* %"idx_ptr.13"
  br label %"if_end.14"
if_else.14:
  %"top_op_load.7" = load i64, i64* %"top_op.1"
  %"icmp.22" = icmp eq i64 %"top_op_load.7", 3
  br i1 %"icmp.22", label %"if_then.15", label %"if_else.15"
if_end.14:
  br label %"if_end.13"
if_then.15:
  %"left_load.6" = load i64, i64* %"left.1"
  %"right_load.6" = load i64, i64* %"right.1"
  %"mul.2" = mul i64 %"left_load.6", %"right_load.6"
  %"values_load.11" = load i64*, i64** %"values"
  %"val_count_load.17" = load i64, i64* %"val_count"
  %"idx_ptr.14" = getelementptr i64, i64* %"values_load.11", i64 %"val_count_load.17"
  store i64 %"mul.2", i64* %"idx_ptr.14"
  br label %"if_end.15"
if_else.15:
  %"top_op_load.8" = load i64, i64* %"top_op.1"
  %"icmp.23" = icmp eq i64 %"top_op_load.8", 4
  br i1 %"icmp.23", label %"if_then.16", label %"if_else.16"
if_end.15:
  br label %"if_end.14"
if_then.16:
  %"left_load.7" = load i64, i64* %"left.1"
  %"right_load.7" = load i64, i64* %"right.1"
  %"div.1" = sdiv i64 %"left_load.7", %"right_load.7"
  %"values_load.12" = load i64*, i64** %"values"
  %"val_count_load.18" = load i64, i64* %"val_count"
  %"idx_ptr.15" = getelementptr i64, i64* %"values_load.12", i64 %"val_count_load.18"
  store i64 %"div.1", i64* %"idx_ptr.15"
  br label %"if_end.16"
if_else.16:
  br label %"if_end.16"
if_end.16:
  br label %"if_end.15"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [10 x i8] c"10+20*3-4\00"
@"str_1" = constant [15 x i8] c"C\c3\b3digo fonte:\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c" \00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c"\0a\00"
@"str_6" = constant [26 x i8] c"Resultado da avalia\c3\a7\c3\a3o:\00"
@"str_7" = constant [3 x i8] c"%s\00"
@"str_8" = constant [2 x i8] c" \00"
@"str_9" = constant [4 x i8] c"%ld\00"
@"str_10" = constant [2 x i8] c"\0a\00"