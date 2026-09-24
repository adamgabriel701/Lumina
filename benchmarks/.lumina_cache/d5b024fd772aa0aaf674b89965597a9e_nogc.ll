; ModuleID = "lumina_module"
target triple = "x86_64-unknown-linux-gnu"
target datalayout = ""

%"Option" = type {i32, i64}
%"Result" = type {i32, i64}
declare i32 @"printf"(i8* %".1", ...)

declare i8* @"malloc"(i64 %".1")

declare void @"free"(i8* %".1")

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
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %"n" = alloca i64
  store i64 1000000, i64* %"n"
  %"argv_load" = load i8**, i8*** @"__lumina_argv"
  %"argv_elem_ptr" = getelementptr i8*, i8** %"argv_load", i64 1
  %"argv_elem" = load i8*, i8** %"argv_elem_ptr"
  %"len_str" = call i64 @"strlen"(i8* %"argv_elem")
  %"icmp" = icmp sgt i64 %"len_str", 0
  br i1 %"icmp", label %"if_then", label %"if_else"
if_then:
  %"argv_load.1" = load i8**, i8*** @"__lumina_argv"
  %"argv_elem_ptr.1" = getelementptr i8*, i8** %"argv_load.1", i64 1
  %"argv_elem.1" = load i8*, i8** %"argv_elem_ptr.1"
  %"atoi_call" = call i64 @"atoi"(i8* %"argv_elem.1")
  store i64 %"atoi_call", i64* %"n"
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"seed" = alloca i64
  store i64 12345, i64* %"seed"
  %"total" = alloca i64
  store i64 0, i64* %"total"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"n_load" = load i64, i64* %"n"
  %"icmp.1" = icmp slt i64 %"i_load", %"n_load"
  br i1 %"icmp.1", label %"while_body", label %"while_end"
while_body:
  %"seed_load" = load i64, i64* %"seed"
  %"mul" = mul i64 %"seed_load", 1103515245
  %"add" = add i64 %"mul", 12345
  %"bitand" = and i64 %"add", 4294967295
  store i64 %"bitand", i64* %"seed"
  %"seed_load.1" = load i64, i64* %"seed"
  %"ashr" = ashr i64 %"seed_load.1", 16
  %"mod" = srem i64 %"ashr", 512
  %"add.1" = add i64 %"mod", 1
  %"size" = alloca i64
  store i64 %"add.1", i64* %"size"
  %"size_load" = load i64, i64* %"size"
  %"alloc_bytes_call" = call i8* @"malloc"(i64 %"size_load")
  %"p" = alloca i8*
  store i8* %"alloc_bytes_call", i8** %"p"
  %"p_load" = load i8*, i8** %"p"
  %"a_null" = icmp eq i8* %"p_load", null
  %"b_null" = icmp eq i8* null, null
  %"either_null" = or i1 %"a_null", %"b_null"
  br i1 %"either_null", label %"strcmp_null", label %"strcmp_ok"
while_end:
  %".32" = bitcast [1 x i8]* @"str_0" to i8*
  %".33" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".33", i8* %".32")
  %"total_load.1" = load i64, i64* %"total"
  %".34" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".34")
  %".35" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".35", i64 %"total_load.1")
  %".36" = bitcast [2 x i8]* @"str_4" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".36")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
strcmp_null:
  %"ptr_ne" = icmp ne i8* %"p_load", null
  br label %"strcmp_end"
strcmp_ok:
  %"strcmp_call" = call i32 @"strcmp"(i8* %"p_load", i8* null)
  %"str_ne" = icmp ne i32 %"strcmp_call", 0
  br label %"strcmp_end"
strcmp_end:
  %"str_cmp_res" = phi  i1 [%"ptr_ne", %"strcmp_null"], [%"str_ne", %"strcmp_ok"]
  br i1 %"str_cmp_res", label %"if_then.1", label %"if_else.1"
if_then.1:
  %"i_load.1" = load i64, i64* %"i"
  %"mod.1" = srem i64 %"i_load.1", 256
  %"p_load.1" = load i8*, i8** %"p"
  %".24" = getelementptr i8, i8* %"p_load.1", i64 0
  %"idx_trunc" = trunc i64 %"mod.1" to i8
  store i8 %"idx_trunc", i8* %".24"
  %"p_load.2" = load i8*, i8** %"p"
  %"ptr_to_int" = ptrtoint i8* %"p_load.2" to i64
  %"black_box_call" = call i64 asm sideeffect "", "=r,0"(i64 %"ptr_to_int")
  %"total_load" = load i64, i64* %"total"
  %"p_load.3" = load i8*, i8** %"p"
  %".26" = getelementptr i8, i8* %"p_load.3", i64 0
  %"ptr_idx_load" = load i8, i8* %".26"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"add.2" = add i64 %"total_load", %"idx_sext"
  store i64 %"add.2", i64* %"total"
  %"p_load.4" = load i8*, i8** %"p"
  call void @"free"(i8* %"p_load.4")
  br label %"if_end.1"
if_else.1:
  br label %"if_end.1"
if_end.1:
  %"i_load.2" = load i64, i64* %"i"
  %"add.3" = add i64 %"i_load.2", 1
  store i64 %"add.3", i64* %"i"
  br label %"while_cond"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [1 x i8] c"\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [2 x i8] c"\0a\00"