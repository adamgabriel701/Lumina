; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
%"StringBuilder" = type {i8*, i64, i64}
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
  %"texto" = alloca i8*
  store i8* %".7", i8** %"texto"
  %".9" = bitcast [54 x i8]* @"str_1" to i8*
  %".10" = bitcast [3 x i8]* @"str_2" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".10", i8* %".9")
  %".11" = bitcast [2 x i8]* @"str_3" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".11")
  %"texto_load" = load i8*, i8** %"texto"
  %".12" = bitcast [7 x i8]* @"str_4" to i8*
  %"str_strstr" = call i8* @"strstr"(i8* %"texto_load", i8* %".12")
  %"str_contains_res" = icmp ne i8* %"str_strstr", null
  %"tem_lumina" = alloca i64
  %"zext_cast" = zext i1 %"str_contains_res" to i64
  store i64 %"zext_cast", i64* %"tem_lumina"
  %".14" = bitcast [18 x i8]* @"str_5" to i8*
  %".15" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".15", i8* %".14")
  %"tem_lumina_load" = load i64, i64* %"tem_lumina"
  %".16" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".16")
  %".17" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".17", i64 %"tem_lumina_load")
  %".18" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %"texto_load.1" = load i8*, i8** %"texto"
  %"to_upper_call" = call i8* @"to_upper"(i8* %"texto_load.1")
  %"maiuscula" = alloca i8*
  store i8* %"to_upper_call", i8** %"maiuscula"
  %".20" = bitcast [10 x i8]* @"str_10" to i8*
  %".21" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".21", i8* %".20")
  %"maiuscula_load" = load i8*, i8** %"maiuscula"
  %".22" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".22")
  %".23" = bitcast [3 x i8]* @"str_13" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".23", i8* %"maiuscula_load")
  %".24" = bitcast [2 x i8]* @"str_14" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %"maiuscula_load.1" = load i8*, i8** %"maiuscula"
  %"to_lower_call" = call i8* @"to_lower"(i8* %"maiuscula_load.1")
  %"minuscula" = alloca i8*
  store i8* %"to_lower_call", i8** %"minuscula"
  %".26" = bitcast [10 x i8]* @"str_15" to i8*
  %".27" = bitcast [3 x i8]* @"str_16" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".27", i8* %".26")
  %"minuscula_load" = load i8*, i8** %"minuscula"
  %".28" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".28")
  %".29" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".29", i8* %"minuscula_load")
  %".30" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %".31" = bitcast [14 x i8]* @"str_20" to i8*
  %"com_espacos" = alloca i8*
  store i8* %".31", i8** %"com_espacos"
  %"com_espacos_load" = load i8*, i8** %"com_espacos"
  %"trim_call" = call i8* @"trim"(i8* %"com_espacos_load")
  %"sem_espacos" = alloca i8*
  store i8* %"trim_call", i8** %"sem_espacos"
  %".34" = bitcast [6 x i8]* @"str_21" to i8*
  %".35" = bitcast [3 x i8]* @"str_22" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".35", i8* %".34")
  %"sem_espacos_load" = load i8*, i8** %"sem_espacos"
  %".36" = bitcast [2 x i8]* @"str_23" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %".37" = bitcast [3 x i8]* @"str_24" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".37", i8* %"sem_espacos_load")
  %".38" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".38")
  %"texto_load.2" = load i8*, i8** %"texto"
  %".39" = bitcast [9 x i8]* @"str_26" to i8*
  %"ends_with_call" = call i64 @"ends_with"(i8* %"texto_load.2", i8* %".39")
  %"acaba_com" = alloca i64
  store i64 %"ends_with_call", i64* %"acaba_com"
  %".41" = bitcast [22 x i8]* @"str_27" to i8*
  %".42" = bitcast [3 x i8]* @"str_28" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".42", i8* %".41")
  %"acaba_com_load" = load i64, i64* %"acaba_com"
  %".43" = bitcast [2 x i8]* @"str_29" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".43")
  %".44" = bitcast [4 x i8]* @"str_30" to i8*
  %"print_call.10" = call i32 (i8*, ...) @"printf"(i8* %".44", i64 %"acaba_com_load")
  %".45" = bitcast [2 x i8]* @"str_31" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".45")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
define i8* @"to_upper"(i8* %".1")
{
to_upper_entry:
  %"s" = alloca i8*
  store i8* %".1", i8** %"s"
  br label %"to_upper_body"
to_upper_body:
  %"new_string_builder_call" = call %"StringBuilder"* @"new_string_builder"()
  %"sb" = alloca %"StringBuilder"*
  store %"StringBuilder"* %"new_string_builder_call", %"StringBuilder"** %"sb"
  %"sb_load" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"s_load" = load i8*, i8** %"s"
  %"len_str" = call i64 @"strlen"(i8* %"s_load")
  %"add" = add i64 %"len_str", 1
  call void @"StringBuilder_reserve"(%"StringBuilder"* %"sb_load", i64 %"add")
  %"s_load.1" = load i8*, i8** %"s"
  %"len_str.1" = call i64 @"strlen"(i8* %"s_load.1")
  %"n" = alloca i64
  store i64 %"len_str.1", i64* %"n"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"s_load.2" = load i8*, i8** %"s"
  %"i_load.1" = load i64, i64* %"i"
  %".10" = getelementptr i8, i8* %"s_load.2", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".10"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"c" = alloca i64
  store i64 %"idx_sext", i64* %"c"
  %"c_load" = load i64, i64* %"c"
  %"icmp.1" = icmp sge i64 %"c_load", 97
  br i1 %"icmp.1", label %"and_rhs", label %"and_end"
while_end:
  %"sb_load.3" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"StringBuilder_finish_call" = call i8* @"StringBuilder_finish"(%"StringBuilder"* %"sb_load.3")
  ret i8* %"StringBuilder_finish_call"
and_rhs:
  %"c_load.1" = load i64, i64* %"c"
  %"icmp.2" = icmp sle i64 %"c_load.1", 122
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_body"], [%"icmp.2", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  %"sb_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"c_load.2" = load i64, i64* %"c"
  %"sub" = sub i64 %"c_load.2", 32
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"sb_load.1", i64 %"sub")
  br label %"if_end"
if_else:
  %"sb_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"c_load.3" = load i64, i64* %"c"
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"sb_load.2", i64 %"c_load.3")
  br label %"if_end"
if_end:
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.2", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
}

define i8* @"to_lower"(i8* %".1")
{
to_lower_entry:
  %"s" = alloca i8*
  store i8* %".1", i8** %"s"
  br label %"to_lower_body"
to_lower_body:
  %"new_string_builder_call" = call %"StringBuilder"* @"new_string_builder"()
  %"sb" = alloca %"StringBuilder"*
  store %"StringBuilder"* %"new_string_builder_call", %"StringBuilder"** %"sb"
  %"sb_load" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"s_load" = load i8*, i8** %"s"
  %"len_str" = call i64 @"strlen"(i8* %"s_load")
  %"add" = add i64 %"len_str", 1
  call void @"StringBuilder_reserve"(%"StringBuilder"* %"sb_load", i64 %"add")
  %"s_load.1" = load i8*, i8** %"s"
  %"len_str.1" = call i64 @"strlen"(i8* %"s_load.1")
  %"n" = alloca i64
  store i64 %"len_str.1", i64* %"n"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"s_load.2" = load i8*, i8** %"s"
  %"i_load.1" = load i64, i64* %"i"
  %".10" = getelementptr i8, i8* %"s_load.2", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".10"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"c" = alloca i64
  store i64 %"idx_sext", i64* %"c"
  %"c_load" = load i64, i64* %"c"
  %"icmp.1" = icmp sge i64 %"c_load", 65
  br i1 %"icmp.1", label %"and_rhs", label %"and_end"
while_end:
  %"sb_load.3" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"StringBuilder_finish_call" = call i8* @"StringBuilder_finish"(%"StringBuilder"* %"sb_load.3")
  ret i8* %"StringBuilder_finish_call"
and_rhs:
  %"c_load.1" = load i64, i64* %"c"
  %"icmp.2" = icmp sle i64 %"c_load.1", 90
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_body"], [%"icmp.2", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  %"sb_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"c_load.2" = load i64, i64* %"c"
  %"add.1" = add i64 %"c_load.2", 32
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"sb_load.1", i64 %"add.1")
  br label %"if_end"
if_else:
  %"sb_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"c_load.3" = load i64, i64* %"c"
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"sb_load.2", i64 %"c_load.3")
  br label %"if_end"
if_end:
  %"i_load.2" = load i64, i64* %"i"
  %"add.2" = add i64 %"i_load.2", 1
  store i64 %"add.2", i64* %"i"
  br label %"while_cond"
}

define i8* @"trim"(i8* %".1")
{
trim_entry:
  %"s" = alloca i8*
  store i8* %".1", i8** %"s"
  br label %"trim_body"
trim_body:
  %"s_load" = load i8*, i8** %"s"
  %"len_str" = call i64 @"strlen"(i8* %"s_load")
  %"length" = alloca i64
  store i64 %"len_str", i64* %"length"
  %"start" = alloca i64
  store i64 0, i64* %"start"
  %"length_load" = load i64, i64* %"length"
  %"sub" = sub i64 %"length_load", 1
  %"end" = alloca i64
  store i64 %"sub", i64* %"end"
  br label %"while_cond"
while_cond:
  %"start_load" = load i64, i64* %"start"
  %"length_load.1" = load i64, i64* %"length"
  %"icmp" = icmp slt i64 %"start_load", %"length_load.1"
  br i1 %"icmp", label %"and_rhs", label %"and_end"
while_body:
  %"start_load.2" = load i64, i64* %"start"
  %"add" = add i64 %"start_load.2", 1
  store i64 %"add", i64* %"start"
  br label %"while_cond"
while_end:
  br label %"while_cond.1"
and_rhs:
  %"s_load.1" = load i8*, i8** %"s"
  %"start_load.1" = load i64, i64* %"start"
  %".10" = getelementptr i8, i8* %"s_load.1", i64 %"start_load.1"
  %"ptr_idx_load" = load i8, i8* %".10"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"icmp.1" = icmp eq i64 %"idx_sext", 32
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_cond"], [%"icmp.1", %"and_rhs"]
  br i1 %"and_result", label %"while_body", label %"while_end"
while_cond.1:
  %"end_load" = load i64, i64* %"end"
  %"icmp.2" = icmp sge i64 %"end_load", 0
  br i1 %"icmp.2", label %"and_rhs.1", label %"and_end.1"
while_body.1:
  %"end_load.2" = load i64, i64* %"end"
  %"sub.1" = sub i64 %"end_load.2", 1
  store i64 %"sub.1", i64* %"end"
  br label %"while_cond.1"
while_end.1:
  %"start_load.3" = load i64, i64* %"start"
  %"end_load.3" = load i64, i64* %"end"
  %"icmp.4" = icmp sgt i64 %"start_load.3", %"end_load.3"
  br i1 %"icmp.4", label %"if_then", label %"if_else"
and_rhs.1:
  %"s_load.2" = load i8*, i8** %"s"
  %"end_load.1" = load i64, i64* %"end"
  %".17" = getelementptr i8, i8* %"s_load.2", i64 %"end_load.1"
  %"ptr_idx_load.1" = load i8, i8* %".17"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"icmp.3" = icmp eq i64 %"idx_sext.1", 32
  br label %"and_end.1"
and_end.1:
  %"and_result.1" = phi  i1 [0, %"while_cond.1"], [%"icmp.3", %"and_rhs.1"]
  br i1 %"and_result.1", label %"while_body.1", label %"while_end.1"
if_then:
  %".23" = bitcast [1 x i8]* @"str_32" to i8*
  ret i8* %".23"
if_else:
  br label %"if_end"
if_end:
  %"s_load.3" = load i8*, i8** %"s"
  %"start_load.4" = load i64, i64* %"start"
  %"end_load.4" = load i64, i64* %"end"
  %"add.1" = add i64 %"end_load.4", 1
  %"slice_len" = sub i64 %"add.1", %"start_load.4"
  %"slice_len_plus" = add i64 %"slice_len", 1
  %"slice_buf" = call i8* @"GC_malloc"(i64 %"slice_len_plus")
  %"slice_start_ptr" = getelementptr i8, i8* %"s_load.3", i64 %"start_load.4"
  %"slice_cpy" = call i8* @"strncpy"(i8* %"slice_buf", i8* %"slice_start_ptr", i64 %"slice_len")
  %"slice_end_ptr" = getelementptr i8, i8* %"slice_buf", i64 %"slice_len"
  store i8 0, i8* %"slice_end_ptr"
  ret i8* %"slice_buf"
}

define i64 @"ends_with"(i8* %".1", i8* %".2")
{
ends_with_entry:
  %"s" = alloca i8*
  store i8* %".1", i8** %"s"
  %"suffix" = alloca i8*
  store i8* %".2", i8** %"suffix"
  br label %"ends_with_body"
ends_with_body:
  %"s_load" = load i8*, i8** %"s"
  %"len_str" = call i64 @"strlen"(i8* %"s_load")
  %"s_len" = alloca i64
  store i64 %"len_str", i64* %"s_len"
  %"suffix_load" = load i8*, i8** %"suffix"
  %"len_str.1" = call i64 @"strlen"(i8* %"suffix_load")
  %"suf_len" = alloca i64
  store i64 %"len_str.1", i64* %"suf_len"
  %"suf_len_load" = load i64, i64* %"suf_len"
  %"s_len_load" = load i64, i64* %"s_len"
  %"icmp" = icmp sgt i64 %"suf_len_load", %"s_len_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"s_load.1" = load i8*, i8** %"s"
  %"s_len_load.1" = load i64, i64* %"s_len"
  %"suf_len_load.1" = load i64, i64* %"suf_len"
  %"sub" = sub i64 %"s_len_load.1", %"suf_len_load.1"
  %"s_len_load.2" = load i64, i64* %"s_len"
  %"slice_len" = sub i64 %"s_len_load.2", %"sub"
  %"slice_len_plus" = add i64 %"slice_len", 1
  %"slice_buf" = call i8* @"GC_malloc"(i64 %"slice_len_plus")
  %"slice_start_ptr" = getelementptr i8, i8* %"s_load.1", i64 %"sub"
  %"slice_cpy" = call i8* @"strncpy"(i8* %"slice_buf", i8* %"slice_start_ptr", i64 %"slice_len")
  %"slice_end_ptr" = getelementptr i8, i8* %"slice_buf", i64 %"slice_len"
  store i8 0, i8* %"slice_end_ptr"
  %"s_end" = alloca i8*
  store i8* %"slice_buf", i8** %"s_end"
  %"s_end_load" = load i8*, i8** %"s_end"
  %"suffix_load.1" = load i8*, i8** %"suffix"
  %"a_null" = icmp eq i8* %"s_end_load", null
  %"b_null" = icmp eq i8* %"suffix_load.1", null
  %"either_null" = or i1 %"a_null", %"b_null"
  br i1 %"either_null", label %"strcmp_null", label %"strcmp_ok"
strcmp_null:
  %"ptr_eq" = icmp eq i8* %"s_end_load", %"suffix_load.1"
  br label %"strcmp_end"
strcmp_ok:
  %"strcmp_call" = call i32 @"strcmp"(i8* %"s_end_load", i8* %"suffix_load.1")
  %"str_eq" = icmp eq i32 %"strcmp_call", 0
  br label %"strcmp_end"
strcmp_end:
  %"str_cmp_res" = phi  i1 [%"ptr_eq", %"strcmp_null"], [%"str_eq", %"strcmp_ok"]
  br i1 %"str_cmp_res", label %"if_then.1", label %"if_else.1"
if_then.1:
  ret i64 1
if_else.1:
  br label %"if_end.1"
if_end.1:
  ret i64 0
}

define i64* @"split"(i8* %".1", i8* %".2")
{
split_entry:
  %"s" = alloca i8*
  store i8* %".1", i8** %"s"
  %"delimiter" = alloca i8*
  store i8* %".2", i8** %"delimiter"
  br label %"split_body"
split_body:
  %"s_load" = load i8*, i8** %"s"
  %"len_str" = call i64 @"strlen"(i8* %"s_load")
  %"length" = alloca i64
  store i64 %"len_str", i64* %"length"
  %"delimiter_load" = load i8*, i8** %"delimiter"
  %"len_str.1" = call i64 @"strlen"(i8* %"delimiter_load")
  %"d_len" = alloca i64
  store i64 %"len_str.1", i64* %"d_len"
  %"alloc_size" = mul i64 100, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"result" = alloca i64*
  %"alloc_bitcast" = bitcast i8* %"alloc_call" to i64*
  store i64* %"alloc_bitcast", i64** %"result"
  %"res_idx" = alloca i64
  store i64 0, i64* %"res_idx"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  %".12" = bitcast [1 x i8]* @"str_33" to i8*
  %"current_word" = alloca i8*
  store i8* %".12", i8** %"current_word"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"length_load" = load i64, i64* %"length"
  %"icmp" = icmp slt i64 %"i_load", %"length_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"s_load.1" = load i8*, i8** %"s"
  %"i_load.1" = load i64, i64* %"i"
  %".16" = getelementptr i8, i8* %"s_load.1", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".16"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"c" = alloca i64
  store i64 %"idx_sext", i64* %"c"
  %"c_load" = load i64, i64* %"c"
  %"delimiter_load.1" = load i8*, i8** %"delimiter"
  %".18" = getelementptr i8, i8* %"delimiter_load.1", i64 0
  %"ptr_idx_load.1" = load i8, i8* %".18"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %"icmp.1" = icmp eq i64 %"c_load", %"idx_sext.1"
  br i1 %"icmp.1", label %"and_rhs", label %"and_end"
while_end:
  %"current_word_load.2" = load i8*, i8** %"current_word"
  %"len_str.2" = call i64 @"strlen"(i8* %"current_word_load.2")
  %"icmp.6" = icmp sgt i64 %"len_str.2", 0
  br i1 %"icmp.6", label %"if_then.3", label %"if_else.3"
and_rhs:
  %"i_load.2" = load i64, i64* %"i"
  %"d_len_load" = load i64, i64* %"d_len"
  %"add" = add i64 %"i_load.2", %"d_len_load"
  %"length_load.1" = load i64, i64* %"length"
  %"icmp.2" = icmp sle i64 %"add", %"length_load.1"
  br label %"and_end"
and_end:
  %"and_result" = phi  i1 [0, %"while_body"], [%"icmp.2", %"and_rhs"]
  br i1 %"and_result", label %"if_then", label %"if_else"
if_then:
  %"is_match" = alloca i64
  store i64 1, i64* %"is_match"
  %"j" = alloca i64
  store i64 1, i64* %"j"
  br label %"while_cond.1"
if_else:
  br label %"if_end"
if_end:
  %"current_word_load.1" = load i8*, i8** %"current_word"
  %"c_load.1" = load i64, i64* %"c"
  %"chr_trunc" = trunc i64 %"c_load.1" to i8
  %"chr_buf" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc", i8* %"chr_buf"
  %"chr_null_ptr" = getelementptr i8, i8* %"chr_buf", i64 1
  store i8 0, i8* %"chr_null_ptr"
  %"sconcat_len1" = call i64 @"strlen"(i8* %"current_word_load.1")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"chr_buf")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"current_word_load.1")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"chr_buf")
  store i8* %"sconcat_buf", i8** %"current_word"
  %"i_load.5" = load i64, i64* %"i"
  %"add.5" = add i64 %"i_load.5", 1
  store i64 %"add.5", i64* %"i"
  br label %"while_cond"
while_cond.1:
  %"j_load" = load i64, i64* %"j"
  %"d_len_load.1" = load i64, i64* %"d_len"
  %"icmp.3" = icmp slt i64 %"j_load", %"d_len_load.1"
  br i1 %"icmp.3", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"s_load.2" = load i8*, i8** %"s"
  %"i_load.3" = load i64, i64* %"i"
  %"j_load.1" = load i64, i64* %"j"
  %"add.1" = add i64 %"i_load.3", %"j_load.1"
  %".26" = getelementptr i8, i8* %"s_load.2", i64 %"add.1"
  %"ptr_idx_load.2" = load i8, i8* %".26"
  %"idx_sext.2" = sext i8 %"ptr_idx_load.2" to i64
  %"delimiter_load.2" = load i8*, i8** %"delimiter"
  %"j_load.2" = load i64, i64* %"j"
  %".27" = getelementptr i8, i8* %"delimiter_load.2", i64 %"j_load.2"
  %"ptr_idx_load.3" = load i8, i8* %".27"
  %"idx_sext.3" = sext i8 %"ptr_idx_load.3" to i64
  %"icmp.4" = icmp ne i64 %"idx_sext.2", %"idx_sext.3"
  br i1 %"icmp.4", label %"if_then.1", label %"if_else.1"
while_end.1:
  %"is_match_load" = load i64, i64* %"is_match"
  %"icmp.5" = icmp eq i64 %"is_match_load", 1
  br i1 %"icmp.5", label %"if_then.2", label %"if_else.2"
if_then.1:
  store i64 0, i64* %"is_match"
  br label %"while_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"j_load.3" = load i64, i64* %"j"
  %"add.2" = add i64 %"j_load.3", 1
  store i64 %"add.2", i64* %"j"
  br label %"while_cond.1"
if_then.2:
  %"current_word_load" = load i8*, i8** %"current_word"
  %"ptr_to_int" = ptrtoint i8* %"current_word_load" to i64
  %"result_load" = load i64*, i64** %"result"
  %"res_idx_load" = load i64, i64* %"res_idx"
  %"idx_ptr" = getelementptr i64, i64* %"result_load", i64 %"res_idx_load"
  store i64 %"ptr_to_int", i64* %"idx_ptr"
  %"res_idx_load.1" = load i64, i64* %"res_idx"
  %"add.3" = add i64 %"res_idx_load.1", 1
  store i64 %"add.3", i64* %"res_idx"
  %".37" = bitcast [1 x i8]* @"str_34" to i8*
  store i8* %".37", i8** %"current_word"
  %"i_load.4" = load i64, i64* %"i"
  %"d_len_load.2" = load i64, i64* %"d_len"
  %"add.4" = add i64 %"i_load.4", %"d_len_load.2"
  store i64 %"add.4", i64* %"i"
  br label %"while_cond"
if_else.2:
  br label %"if_end.2"
if_end.2:
  br label %"if_end"
if_then.3:
  %"current_word_load.3" = load i8*, i8** %"current_word"
  %"ptr_to_int.1" = ptrtoint i8* %"current_word_load.3" to i64
  %"result_load.1" = load i64*, i64** %"result"
  %"res_idx_load.2" = load i64, i64* %"res_idx"
  %"idx_ptr.1" = getelementptr i64, i64* %"result_load.1", i64 %"res_idx_load.2"
  store i64 %"ptr_to_int.1", i64* %"idx_ptr.1"
  %"res_idx_load.3" = load i64, i64* %"res_idx"
  %"add.6" = add i64 %"res_idx_load.3", 1
  store i64 %"add.6", i64* %"res_idx"
  br label %"if_end.3"
if_else.3:
  br label %"if_end.3"
if_end.3:
  %"result_load.2" = load i64*, i64** %"result"
  %"res_idx_load.4" = load i64, i64* %"res_idx"
  %"idx_ptr.2" = getelementptr i64, i64* %"result_load.2", i64 %"res_idx_load.4"
  store i64 0, i64* %"idx_ptr.2"
  %"result_load.3" = load i64*, i64** %"result"
  ret i64* %"result_load.3"
}

define i8* @"join"(i64* %".1", i8* %".2")
{
join_entry:
  %"arr" = alloca i64*
  store i64* %".1", i64** %"arr"
  %"delimiter" = alloca i8*
  store i8* %".2", i8** %"delimiter"
  br label %"join_body"
join_body:
  %".7" = bitcast [1 x i8]* @"str_35" to i8*
  %"res" = alloca i8*
  store i8* %".7", i8** %"res"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"arr_load" = load i64*, i64** %"arr"
  %"i_load" = load i64, i64* %"i"
  %".11" = getelementptr i64, i64* %"arr_load", i64 %"i_load"
  %"ptr_idx_load" = load i64, i64* %".11"
  %"icmp" = icmp ne i64 %"ptr_idx_load", 0
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"res_load" = load i8*, i8** %"res"
  %"len_str" = call i64 @"strlen"(i8* %"res_load")
  %"icmp.1" = icmp sgt i64 %"len_str", 0
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"res_load.3" = load i8*, i8** %"res"
  ret i8* %"res_load.3"
if_then:
  %"res_load.1" = load i8*, i8** %"res"
  %"delimiter_load" = load i8*, i8** %"delimiter"
  %"sconcat_len1" = call i64 @"strlen"(i8* %"res_load.1")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"delimiter_load")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"res_load.1")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"delimiter_load")
  store i8* %"sconcat_buf", i8** %"res"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"res_load.2" = load i8*, i8** %"res"
  %"arr_load.1" = load i64*, i64** %"arr"
  %"i_load.1" = load i64, i64* %"i"
  %".17" = getelementptr i64, i64* %"arr_load.1", i64 %"i_load.1"
  %"ptr_idx_load.1" = load i64, i64* %".17"
  %"int_to_ptr" = inttoptr i64 %"ptr_idx_load.1" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"res_load.2")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %"int_to_ptr")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"res_load.2")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %"int_to_ptr")
  store i8* %"sconcat_buf.1", i8** %"res"
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

define i8* @"substr"(i8* %".1", i64 %".2", i64 %".3")
{
substr_entry:
  %"s" = alloca i8*
  store i8* %".1", i8** %"s"
  %"start" = alloca i64
  store i64 %".2", i64* %"start"
  %"length" = alloca i64
  store i64 %".3", i64* %"length"
  br label %"substr_body"
substr_body:
  %"s_load" = load i8*, i8** %"s"
  %"start_load" = load i64, i64* %"start"
  %"start_load.1" = load i64, i64* %"start"
  %"length_load" = load i64, i64* %"length"
  %"add" = add i64 %"start_load.1", %"length_load"
  %"slice_len" = sub i64 %"add", %"start_load"
  %"slice_len_plus" = add i64 %"slice_len", 1
  %"slice_buf" = call i8* @"GC_malloc"(i64 %"slice_len_plus")
  %"slice_start_ptr" = getelementptr i8, i8* %"s_load", i64 %"start_load"
  %"slice_cpy" = call i8* @"strncpy"(i8* %"slice_buf", i8* %"slice_start_ptr", i64 %"slice_len")
  %"slice_end_ptr" = getelementptr i8, i8* %"slice_buf", i64 %"slice_len"
  store i8 0, i8* %"slice_end_ptr"
  ret i8* %"slice_buf"
}

define i64 @"find"(i8* %".1", i8* %".2")
{
find_entry:
  %"texto" = alloca i8*
  store i8* %".1", i8** %"texto"
  %"alvo" = alloca i8*
  store i8* %".2", i8** %"alvo"
  br label %"find_body"
find_body:
  %"texto_load" = load i8*, i8** %"texto"
  %"len_str" = call i64 @"strlen"(i8* %"texto_load")
  %"n" = alloca i64
  store i64 %"len_str", i64* %"n"
  %"alvo_load" = load i8*, i8** %"alvo"
  %"len_str.1" = call i64 @"strlen"(i8* %"alvo_load")
  %"m" = alloca i64
  store i64 %"len_str.1", i64* %"m"
  %"m_load" = load i64, i64* %"m"
  %"icmp" = icmp eq i64 %"m_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  ret i64 0
if_else:
  br label %"if_end"
if_end:
  %"m_load.1" = load i64, i64* %"m"
  %"n_load" = load i64, i64* %"n"
  %"icmp.1" = icmp sgt i64 %"m_load.1", %"n_load"
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"neg" = sub i64 0, 1
  ret i64 %"neg"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load.1" = load i64, i64* %"n"
  %"m_load.2" = load i64, i64* %"m"
  %"sub" = sub i64 %"n_load.1", %"m_load.2"
  %"icmp.2" = icmp sle i64 %"i_load", %"sub"
  br i1 %"icmp.2", label %"while_body", label %"while_end"
while_body:
  %"texto_load.1" = load i8*, i8** %"texto"
  %"i_load.1" = load i64, i64* %"i"
  %"i_load.2" = load i64, i64* %"i"
  %"m_load.3" = load i64, i64* %"m"
  %"add" = add i64 %"i_load.2", %"m_load.3"
  %"slice_len" = sub i64 %"add", %"i_load.1"
  %"slice_len_plus" = add i64 %"slice_len", 1
  %"slice_buf" = call i8* @"GC_malloc"(i64 %"slice_len_plus")
  %"slice_start_ptr" = getelementptr i8, i8* %"texto_load.1", i64 %"i_load.1"
  %"slice_cpy" = call i8* @"strncpy"(i8* %"slice_buf", i8* %"slice_start_ptr", i64 %"slice_len")
  %"slice_end_ptr" = getelementptr i8, i8* %"slice_buf", i64 %"slice_len"
  store i8 0, i8* %"slice_end_ptr"
  %"alvo_load.1" = load i8*, i8** %"alvo"
  %"a_null" = icmp eq i8* %"slice_buf", null
  %"b_null" = icmp eq i8* %"alvo_load.1", null
  %"either_null" = or i1 %"a_null", %"b_null"
  br i1 %"either_null", label %"strcmp_null", label %"strcmp_ok"
while_end:
  %"neg.1" = sub i64 0, 1
  ret i64 %"neg.1"
strcmp_null:
  %"ptr_eq" = icmp eq i8* %"slice_buf", %"alvo_load.1"
  br label %"strcmp_end"
strcmp_ok:
  %"strcmp_call" = call i32 @"strcmp"(i8* %"slice_buf", i8* %"alvo_load.1")
  %"str_eq" = icmp eq i32 %"strcmp_call", 0
  br label %"strcmp_end"
strcmp_end:
  %"str_cmp_res" = phi  i1 [%"ptr_eq", %"strcmp_null"], [%"str_eq", %"strcmp_ok"]
  br i1 %"str_cmp_res", label %"if_then.2", label %"if_else.2"
if_then.2:
  %"i_load.3" = load i64, i64* %"i"
  ret i64 %"i_load.3"
if_else.2:
  br label %"if_end.2"
if_end.2:
  %"i_load.4" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.4", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
}

define void @"StringBuilder_reserve"(%"StringBuilder"* %".1", i64 %".2")
{
StringBuilder_reserve_entry:
  %"self" = alloca %"StringBuilder"*
  store %"StringBuilder"* %".1", %"StringBuilder"** %"self"
  %"min_cap" = alloca i64
  store i64 %".2", i64* %"min_cap"
  br label %"StringBuilder_reserve_body"
StringBuilder_reserve_body:
  %"min_cap_load" = load i64, i64* %"min_cap"
  %"self_load" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".7" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load", i32 0, i32 2
  %"cap_load" = load i64, i64* %".7"
  %"icmp" = icmp sle i64 %"min_cap_load", %"cap_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  ret void
if_else:
  br label %"if_end"
if_end:
  %"self_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".11" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.1", i32 0, i32 2
  %"cap_load.1" = load i64, i64* %".11"
  %"new_cap" = alloca i64
  store i64 %"cap_load.1", i64* %"new_cap"
  %"new_cap_load" = load i64, i64* %"new_cap"
  %"icmp.1" = icmp eq i64 %"new_cap_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  store i64 32, i64* %"new_cap"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  br label %"while_cond"
while_cond:
  %"new_cap_load.1" = load i64, i64* %"new_cap"
  %"min_cap_load.1" = load i64, i64* %"min_cap"
  %"icmp.2" = icmp slt i64 %"new_cap_load.1", %"min_cap_load.1"
  br i1 %"icmp.2", label %"while_body", label %"while_end"
while_body:
  %"new_cap_load.2" = load i64, i64* %"new_cap"
  %"mul" = mul i64 %"new_cap_load.2", 2
  store i64 %"mul", i64* %"new_cap"
  br label %"while_cond"
while_end:
  %"new_cap_load.3" = load i64, i64* %"new_cap"
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 %"new_cap_load.3")
  %"new_buf" = alloca i8*
  store i8* %"alloc_bytes_call", i8** %"new_buf"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond.1"
while_cond.1:
  %"i_load" = load i64, i64* %"i"
  %"self_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".24" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.2", i32 0, i32 1
  %"len_load" = load i64, i64* %".24"
  %"icmp.3" = icmp slt i64 %"i_load", %"len_load"
  br i1 %"icmp.3", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"self_load.3" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".26" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.3", i32 0, i32 0
  %"buf_load" = load i8*, i8** %".26"
  %"i_load.1" = load i64, i64* %"i"
  %".27" = getelementptr i8, i8* %"buf_load", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".27"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"new_buf_load" = load i8*, i8** %"new_buf"
  %"i_load.2" = load i64, i64* %"i"
  %"idx_ptr" = getelementptr i8, i8* %"new_buf_load", i64 %"i_load.2"
  %"elem_trunc" = trunc i64 %"idx_sext" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"i_load.3" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.3", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond.1"
while_end.1:
  %"new_buf_load.1" = load i8*, i8** %"new_buf"
  %"self_load.4" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"buf_ptr" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.4", i32 0, i32 0
  store i8* %"new_buf_load.1", i8** %"buf_ptr"
  %"new_cap_load.4" = load i64, i64* %"new_cap"
  %"self_load.5" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"cap_ptr" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.5", i32 0, i32 2
  store i64 %"new_cap_load.4", i64* %"cap_ptr"
  ret void
}

define void @"StringBuilder_push_char"(%"StringBuilder"* %".1", i64 %".2")
{
StringBuilder_push_char_entry:
  %"self" = alloca %"StringBuilder"*
  store %"StringBuilder"* %".1", %"StringBuilder"** %"self"
  %"c" = alloca i64
  store i64 %".2", i64* %"c"
  br label %"StringBuilder_push_char_body"
StringBuilder_push_char_body:
  %"self_load" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".7" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load", i32 0, i32 1
  %"len_load" = load i64, i64* %".7"
  %"self_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".8" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.1", i32 0, i32 2
  %"cap_load" = load i64, i64* %".8"
  %"icmp" = icmp sge i64 %"len_load", %"cap_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"self_load.3" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".10" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.3", i32 0, i32 1
  %"len_load.1" = load i64, i64* %".10"
  %"add" = add i64 %"len_load.1", 1
  call void @"StringBuilder_reserve"(%"StringBuilder"* %"self_load.2", i64 %"add")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"c_load" = load i64, i64* %"c"
  %"self_load.4" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".13" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.4", i32 0, i32 0
  %"buf_load" = load i8*, i8** %".13"
  %"self_load.5" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".14" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.5", i32 0, i32 1
  %"len_load.2" = load i64, i64* %".14"
  %"idx_ptr" = getelementptr i8, i8* %"buf_load", i64 %"len_load.2"
  %"elem_trunc" = trunc i64 %"c_load" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"self_load.6" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".16" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.6", i32 0, i32 1
  %"len_load.3" = load i64, i64* %".16"
  %"add.1" = add i64 %"len_load.3", 1
  %"self_load.7" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"len_ptr" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.7", i32 0, i32 1
  store i64 %"add.1", i64* %"len_ptr"
  ret void
}

define void @"StringBuilder_push_str"(%"StringBuilder"* %".1", i8* %".2")
{
StringBuilder_push_str_entry:
  %"self" = alloca %"StringBuilder"*
  store %"StringBuilder"* %".1", %"StringBuilder"** %"self"
  %"s" = alloca i8*
  store i8* %".2", i8** %"s"
  br label %"StringBuilder_push_str_body"
StringBuilder_push_str_body:
  %"s_load" = load i8*, i8** %"s"
  %"len_str" = call i64 @"strlen"(i8* %"s_load")
  %"n" = alloca i64
  store i64 %"len_str", i64* %"n"
  %"self_load" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"self_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".8" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.1", i32 0, i32 1
  %"len_load" = load i64, i64* %".8"
  %"n_load" = load i64, i64* %"n"
  %"add" = add i64 %"len_load", %"n_load"
  call void @"StringBuilder_reserve"(%"StringBuilder"* %"self_load", i64 %"add")
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load.1" = load i64, i64* %"n"
  %"icmp" = icmp slt i64 %"i_load", %"n_load.1"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"s_load.1" = load i8*, i8** %"s"
  %"i_load.1" = load i64, i64* %"i"
  %".12" = getelementptr i8, i8* %"s_load.1", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".12"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"self_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".13" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.2", i32 0, i32 0
  %"buf_load" = load i8*, i8** %".13"
  %"self_load.3" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".14" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.3", i32 0, i32 1
  %"len_load.1" = load i64, i64* %".14"
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"len_load.1", %"i_load.2"
  %"idx_ptr" = getelementptr i8, i8* %"buf_load", i64 %"add.1"
  %"elem_trunc" = trunc i64 %"idx_sext" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"i_load.3" = load i64, i64* %"i"
  %"add.2" = add i64 %"i_load.3", 1
  store i64 %"add.2", i64* %"i"
  br label %"while_cond"
while_end:
  %"self_load.4" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".18" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.4", i32 0, i32 1
  %"len_load.2" = load i64, i64* %".18"
  %"n_load.2" = load i64, i64* %"n"
  %"add.3" = add i64 %"len_load.2", %"n_load.2"
  %"self_load.5" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"len_ptr" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.5", i32 0, i32 1
  store i64 %"add.3", i64* %"len_ptr"
  ret void
}

define void @"StringBuilder_push_int"(%"StringBuilder"* %".1", i64 %".2")
{
StringBuilder_push_int_entry:
  %"self" = alloca %"StringBuilder"*
  store %"StringBuilder"* %".1", %"StringBuilder"** %"self"
  %"v" = alloca i64
  store i64 %".2", i64* %"v"
  br label %"StringBuilder_push_int_body"
StringBuilder_push_int_body:
  %"v_load" = load i64, i64* %"v"
  %"icmp" = icmp eq i64 %"v_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"self_load", i64 48)
  ret void
if_else:
  br label %"if_end"
if_end:
  %"v_load.1" = load i64, i64* %"v"
  %"n" = alloca i64
  store i64 %"v_load.1", i64* %"n"
  %"n_load" = load i64, i64* %"n"
  %"icmp.1" = icmp slt i64 %"n_load", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"self_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"self_load.1", i64 45)
  %"n_load.1" = load i64, i64* %"n"
  %"neg" = sub i64 0, %"n_load.1"
  store i64 %"neg", i64* %"n"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"digits_stack" = alloca [20 x i8]
  %"digits_first" = getelementptr [20 x i8], [20 x i8]* %"digits_stack", i32 0, i32 0
  %"digits" = alloca i8*
  store i8* %"digits_first", i8** %"digits"
  %"count" = alloca i64
  store i64 0, i64* %"count"
  br label %"while_cond"
while_cond:
  %"n_load.2" = load i64, i64* %"n"
  %"icmp.2" = icmp sgt i64 %"n_load.2", 0
  br i1 %"icmp.2", label %"while_body", label %"while_end"
while_body:
  %"n_load.3" = load i64, i64* %"n"
  %"mod" = srem i64 %"n_load.3", 10
  %"add" = add i64 48, %"mod"
  %"digits_load" = load i8*, i8** %"digits"
  %"count_load" = load i64, i64* %"count"
  %"idx_ptr" = getelementptr i8, i8* %"digits_load", i64 %"count_load"
  %"elem_trunc" = trunc i64 %"add" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"n_load.4" = load i64, i64* %"n"
  %"div" = sdiv i64 %"n_load.4", 10
  store i64 %"div", i64* %"n"
  %"count_load.1" = load i64, i64* %"count"
  %"add.1" = add i64 %"count_load.1", 1
  store i64 %"add.1", i64* %"count"
  br label %"while_cond"
while_end:
  %"count_load.2" = load i64, i64* %"count"
  %"sub" = sub i64 %"count_load.2", 1
  %"i" = alloca i64
  store i64 %"sub", i64* %"i"
  br label %"while_cond.1"
while_cond.1:
  %"i_load" = load i64, i64* %"i"
  %"icmp.3" = icmp sge i64 %"i_load", 0
  br i1 %"icmp.3", label %"while_body.1", label %"while_end.1"
while_body.1:
  %"self_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"digits_load.1" = load i8*, i8** %"digits"
  %"i_load.1" = load i64, i64* %"i"
  %".26" = getelementptr i8, i8* %"digits_load.1", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".26"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"self_load.2", i64 %"idx_sext")
  %"i_load.2" = load i64, i64* %"i"
  %"sub.1" = sub i64 %"i_load.2", 1
  store i64 %"sub.1", i64* %"i"
  br label %"while_cond.1"
while_end.1:
  ret void
}

define void @"StringBuilder_push_float"(%"StringBuilder"* %".1", double %".2")
{
StringBuilder_push_float_entry:
  %"self" = alloca %"StringBuilder"*
  store %"StringBuilder"* %".1", %"StringBuilder"** %"self"
  %"v" = alloca double
  store double %".2", double* %"v"
  br label %"StringBuilder_push_float_body"
StringBuilder_push_float_body:
  %"v_load" = load double, double* %"v"
  %"float_to_int" = fptosi double %"v_load" to i64
  %"inteiro" = alloca i64
  store i64 %"float_to_int", i64* %"inteiro"
  %"self_load" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"inteiro_load" = load i64, i64* %"inteiro"
  call void @"StringBuilder_push_int"(%"StringBuilder"* %"self_load", i64 %"inteiro_load")
  %"self_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"self_load.1", i64 46)
  %"v_load.1" = load double, double* %"v"
  %"inteiro_load.1" = load i64, i64* %"inteiro"
  %"int_to_float" = sitofp i64 %"inteiro_load.1" to double
  %"fsub" = fsub double %"v_load.1", %"int_to_float"
  %"frac" = alloca double
  store double %"fsub", double* %"frac"
  %"frac_load" = load double, double* %"frac"
  %"fcmp" = fcmp olt double %"frac_load",              0x0
  br i1 %"fcmp", label %"if_then", label %"if_else"
if_then:
  %"frac_load.1" = load double, double* %"frac"
  %"fneg" = fneg double %"frac_load.1"
  store double %"fneg", double* %"frac"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"icmp" = icmp slt i64 %"i_load", 6
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"frac_load.2" = load double, double* %"frac"
  %"fmul" = fmul double %"frac_load.2", 0x4024000000000000
  store double %"fmul", double* %"frac"
  %"frac_load.3" = load double, double* %"frac"
  %"float_to_int.1" = fptosi double %"frac_load.3" to i64
  %"dig" = alloca i64
  store i64 %"float_to_int.1", i64* %"dig"
  %"self_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"dig_load" = load i64, i64* %"dig"
  %"mod" = srem i64 %"dig_load", 10
  %"add" = add i64 48, %"mod"
  call void @"StringBuilder_push_char"(%"StringBuilder"* %"self_load.2", i64 %"add")
  %"frac_load.4" = load double, double* %"frac"
  %"dig_load.1" = load i64, i64* %"dig"
  %"int_to_float.1" = sitofp i64 %"dig_load.1" to double
  %"fsub.1" = fsub double %"frac_load.4", %"int_to_float.1"
  store double %"fsub.1", double* %"frac"
  %"i_load.1" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.1", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  ret void
}

define i8* @"StringBuilder_finish"(%"StringBuilder"* %".1")
{
StringBuilder_finish_entry:
  %"self" = alloca %"StringBuilder"*
  store %"StringBuilder"* %".1", %"StringBuilder"** %"self"
  br label %"StringBuilder_finish_body"
StringBuilder_finish_body:
  %"self_load" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".5" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load", i32 0, i32 1
  %"len_load" = load i64, i64* %".5"
  %"self_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".6" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.1", i32 0, i32 2
  %"cap_load" = load i64, i64* %".6"
  %"icmp" = icmp sge i64 %"len_load", %"cap_load"
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"self_load.3" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".8" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.3", i32 0, i32 1
  %"len_load.1" = load i64, i64* %".8"
  %"add" = add i64 %"len_load.1", 1
  call void @"StringBuilder_reserve"(%"StringBuilder"* %"self_load.2", i64 %"add")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"self_load.4" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".11" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.4", i32 0, i32 0
  %"buf_load" = load i8*, i8** %".11"
  %"self_load.5" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".12" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.5", i32 0, i32 1
  %"len_load.2" = load i64, i64* %".12"
  %"idx_ptr" = getelementptr i8, i8* %"buf_load", i64 %"len_load.2"
  %"elem_trunc" = trunc i64 0 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"self_load.6" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".14" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.6", i32 0, i32 0
  %"buf_load.1" = load i8*, i8** %".14"
  ret i8* %"buf_load.1"
}

define void @"StringBuilder_clear"(%"StringBuilder"* %".1")
{
StringBuilder_clear_entry:
  %"self" = alloca %"StringBuilder"*
  store %"StringBuilder"* %".1", %"StringBuilder"** %"self"
  br label %"StringBuilder_clear_body"
StringBuilder_clear_body:
  %"self_load" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %"len_ptr" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load", i32 0, i32 1
  store i64 0, i64* %"len_ptr"
  %"self_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".6" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.1", i32 0, i32 2
  %"cap_load" = load i64, i64* %".6"
  %"icmp" = icmp sgt i64 %"cap_load", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"self_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".8" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load.2", i32 0, i32 0
  %"buf_load" = load i8*, i8** %".8"
  %"idx_ptr" = getelementptr i8, i8* %"buf_load", i64 0
  %"elem_trunc" = trunc i64 0 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  ret void
}

define i64 @"StringBuilder_size"(%"StringBuilder"* %".1")
{
StringBuilder_size_entry:
  %"self" = alloca %"StringBuilder"*
  store %"StringBuilder"* %".1", %"StringBuilder"** %"self"
  br label %"StringBuilder_size_body"
StringBuilder_size_body:
  %"self_load" = load %"StringBuilder"*, %"StringBuilder"** %"self"
  %".5" = getelementptr %"StringBuilder", %"StringBuilder"* %"self_load", i32 0, i32 1
  %"len_load" = load i64, i64* %".5"
  ret i64 %"len_load"
}

define %"StringBuilder"* @"new_string_builder"()
{
new_string_builder_entry:
  br label %"new_string_builder_body"
new_string_builder_body:
  %"sb" = alloca %"StringBuilder"*
  %"sb_storage_raw" = call i8* @"GC_malloc"(i64 24)
  %"sb_storage" = bitcast i8* %"sb_storage_raw" to %"StringBuilder"*
  store %"StringBuilder" {i8* null, i64 0, i64 0}, %"StringBuilder"* %"sb_storage"
  store %"StringBuilder"* %"sb_storage", %"StringBuilder"** %"sb"
  %"sb_load" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"cap_ptr" = getelementptr %"StringBuilder", %"StringBuilder"* %"sb_load", i32 0, i32 2
  store i64 32, i64* %"cap_ptr"
  %"sb_load.1" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"len_ptr" = getelementptr %"StringBuilder", %"StringBuilder"* %"sb_load.1", i32 0, i32 1
  store i64 0, i64* %"len_ptr"
  %"alloc_bytes_call" = call i8* @"GC_malloc"(i64 32)
  %"sb_load.2" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %"buf_ptr" = getelementptr %"StringBuilder", %"StringBuilder"* %"sb_load.2", i32 0, i32 0
  store i8* %"alloc_bytes_call", i8** %"buf_ptr"
  %"sb_load.3" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  %".8" = getelementptr %"StringBuilder", %"StringBuilder"* %"sb_load.3", i32 0, i32 0
  %"buf_load" = load i8*, i8** %".8"
  %"idx_ptr" = getelementptr i8, i8* %"buf_load", i64 0
  %"elem_trunc" = trunc i64 0 to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"sb_load.4" = load %"StringBuilder"*, %"StringBuilder"** %"sb"
  ret %"StringBuilder"* %"sb_load.4"
}

@"str_0" = constant [16 x i8] c"Lumina Language\00"
@"str_1" = constant [54 x i8] c"Testando a Standard Library Nativa (Bootstrapping)...\00"
@"str_2" = constant [3 x i8] c"%s\00"
@"str_3" = constant [2 x i8] c"\0a\00"
@"str_4" = constant [7 x i8] c"Lumina\00"
@"str_5" = constant [18 x i8] c"Cont\c3\a9m 'Lumina'?\00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [10 x i8] c"To Upper:\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c" \00"
@"str_13" = constant [3 x i8] c"%s\00"
@"str_14" = constant [2 x i8] c"\0a\00"
@"str_15" = constant [10 x i8] c"To Lower:\00"
@"str_16" = constant [3 x i8] c"%s\00"
@"str_17" = constant [2 x i8] c" \00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c"\0a\00"
@"str_20" = constant [14 x i8] c"   espacos   \00"
@"str_21" = constant [6 x i8] c"Trim:\00"
@"str_22" = constant [3 x i8] c"%s\00"
@"str_23" = constant [2 x i8] c" \00"
@"str_24" = constant [3 x i8] c"%s\00"
@"str_25" = constant [2 x i8] c"\0a\00"
@"str_26" = constant [9 x i8] c"Language\00"
@"str_27" = constant [22 x i8] c"Ends with 'Language'?\00"
@"str_28" = constant [3 x i8] c"%s\00"
@"str_29" = constant [2 x i8] c" \00"
@"str_30" = constant [4 x i8] c"%ld\00"
@"str_31" = constant [2 x i8] c"\0a\00"
@"str_32" = constant [1 x i8] c"\00"
@"str_33" = constant [1 x i8] c"\00"
@"str_34" = constant [1 x i8] c"\00"
@"str_35" = constant [1 x i8] c"\00"