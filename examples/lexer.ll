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
  %".7" = bitcast [11 x i8]* @"str_0" to i8*
  %"code" = alloca i8*
  store i8* %".7", i8** %"code"
  %"code_load" = load i8*, i8** %"code"
  %"len_str" = call i64 @"strlen"(i8* %"code_load")
  %"length" = alloca i64
  store i64 %"len_str", i64* %"length"
  %".10" = bitcast [1 x i8]* @"str_1" to i8*
  %"token" = alloca i8*
  store i8* %".10", i8** %"token"
  %"length_load" = load i64, i64* %"length"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"for_cond"
for_cond:
  %"for_curr" = load i64, i64* %"i"
  %"for_cond.1" = icmp slt i64 %"for_curr", %"length_load"
  br i1 %"for_cond.1", label %"for_body", label %"for_end"
for_body:
  %"code_load.1" = load i8*, i8** %"code"
  %"i_load" = load i64, i64* %"i"
  %".15" = getelementptr i8, i8* %"code_load.1", i64 %"i_load"
  %"ptr_idx_load" = load i8, i8* %".15"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"c" = alloca i64
  store i64 %"idx_sext", i64* %"c"
  %"c_load" = load i64, i64* %"c"
  %"icmp" = icmp eq i64 %"c_load", 32
  br i1 %"icmp", label %"if_then", label %"if_else"
for_inc:
  %"for_curr_inc" = load i64, i64* %"i"
  %"for_next" = add i64 %"for_curr_inc", 1
  store i64 %"for_next", i64* %"i"
  br label %"for_cond"
for_end:
  %"token_load.3" = load i8*, i8** %"token"
  %"len_str.2" = call i64 @"strlen"(i8* %"token_load.3")
  %"icmp.2" = icmp sgt i64 %"len_str.2", 0
  br i1 %"icmp.2", label %"if_then.2", label %"if_else.2"
if_then:
  %"token_load" = load i8*, i8** %"token"
  %"len_str.1" = call i64 @"strlen"(i8* %"token_load")
  %"icmp.1" = icmp sgt i64 %"len_str.1", 0
  br i1 %"icmp.1", label %"if_then.1", label %"if_else.1"
if_else:
  %"token_load.2" = load i8*, i8** %"token"
  %"c_load.1" = load i64, i64* %"c"
  %"chr_trunc" = trunc i64 %"c_load.1" to i8
  %"chr_buf" = call i8* @"GC_malloc"(i64 2)
  store i8 %"chr_trunc", i8* %"chr_buf"
  %"chr_null_ptr" = getelementptr i8, i8* %"chr_buf", i64 1
  store i8 0, i8* %"chr_null_ptr"
  %"sconcat_len1" = call i64 @"strlen"(i8* %"token_load.2")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"chr_buf")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"token_load.2")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"chr_buf")
  store i8* %"sconcat_buf", i8** %"token"
  br label %"if_end"
if_end:
  br label %"for_inc"
if_then.1:
  %".19" = bitcast [7 x i8]* @"str_2" to i8*
  %".20" = bitcast [3 x i8]* @"str_3" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %"token_load.1" = load i8*, i8** %"token"
  %".21" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [3 x i8]* @"str_5" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".22", i8* %"token_load.1")
  %".23" = bitcast [2 x i8]* @"str_6" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".23")
  %".24" = bitcast [1 x i8]* @"str_7" to i8*
  store i8* %".24", i8** %"token"
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  br label %"if_end"
if_then.2:
  %".37" = bitcast [7 x i8]* @"str_8" to i8*
  %".38" = bitcast [3 x i8]* @"str_9" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".38", i8* %".37")
  %"token_load.4" = load i8*, i8** %"token"
  %".39" = bitcast [2 x i8]* @"str_10" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".39")
  %".40" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".40", i8* %"token_load.4")
  %".41" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".41")
  br label %"if_end.2"
if_else.2:
  br label %"if_end.2"
if_end.2:
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [11 x i8] c"let x = 42\00"
@"str_1" = constant [1 x i8] c"\00"
@"str_2" = constant [7 x i8] c"Token:\00"
@"str_3" = constant [3 x i8] c"%s\00"
@"str_4" = constant [2 x i8] c" \00"
@"str_5" = constant [3 x i8] c"%s\00"
@"str_6" = constant [2 x i8] c"\0a\00"
@"str_7" = constant [1 x i8] c"\00"
@"str_8" = constant [7 x i8] c"Token:\00"
@"str_9" = constant [3 x i8] c"%s\00"
@"str_10" = constant [2 x i8] c" \00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c"\0a\00"