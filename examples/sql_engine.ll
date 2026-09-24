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
@"g_row_count" = internal global i64 0
define void @"insert"(i64 %".1", i64 %".2", i64 %".3")
{
insert_entry:
  %"id" = alloca i64
  store i64 %".1", i64* %"id"
  %"age" = alloca i64
  store i64 %".2", i64* %"age"
  %"salary" = alloca i64
  store i64 %".3", i64* %"salary"
  br label %"insert_body"
insert_body:
  %"id_load" = load i64, i64* %"id"
  %"alloc_size" = mul i64 1000, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"g_row_count_load" = load i64, i64* @"g_row_count"
  %"idx_ptr" = getelementptr i8, i8* %"alloc_call", i64 %"g_row_count_load"
  %"elem_trunc" = trunc i64 %"id_load" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %"age_load" = load i64, i64* %"age"
  %"alloc_size.1" = mul i64 1000, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"g_row_count_load.1" = load i64, i64* @"g_row_count"
  %"idx_ptr.1" = getelementptr i8, i8* %"alloc_call.1", i64 %"g_row_count_load.1"
  %"elem_trunc.1" = trunc i64 %"age_load" to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  %"salary_load" = load i64, i64* %"salary"
  %"alloc_size.2" = mul i64 1000, 8
  %"alloc_call.2" = call i8* @"GC_malloc"(i64 %"alloc_size.2")
  %"g_row_count_load.2" = load i64, i64* @"g_row_count"
  %"idx_ptr.2" = getelementptr i8, i8* %"alloc_call.2", i64 %"g_row_count_load.2"
  %"elem_trunc.2" = trunc i64 %"salary_load" to i8
  store i8 %"elem_trunc.2", i8* %"idx_ptr.2"
  %"g_row_count_load.3" = load i64, i64* @"g_row_count"
  %"add" = add i64 %"g_row_count_load.3", 1
  store i64 %"add", i64* @"g_row_count"
  ret void
}

define void @"select_all"()
{
select_all_entry:
  br label %"select_all_body"
select_all_body:
  %".3" = bitcast [18 x i8]* @"str_0" to i8*
  %".4" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".4", i8* %".3")
  %".5" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".5")
  %".6" = bitcast [19 x i8]* @"str_3" to i8*
  %".7" = bitcast [3 x i8]* @"str_4" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".7", i8* %".6")
  %".8" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".8")
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"g_row_count_load" = load i64, i64* @"g_row_count"
  %"icmp" = icmp slt i64 %"i_load", %"g_row_count_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"alloc_size" = mul i64 1000, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"i_load.1" = load i64, i64* %"i"
  %".12" = getelementptr i8, i8* %"alloc_call", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".12"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %".13" = bitcast [4 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".13", i64 %"idx_sext")
  %"alloc_size.1" = mul i64 1000, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"i_load.2" = load i64, i64* %"i"
  %".14" = getelementptr i8, i8* %"alloc_call.1", i64 %"i_load.2"
  %"ptr_idx_load.1" = load i8, i8* %".14"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %".15" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".16", i64 %"idx_sext.1")
  %"alloc_size.2" = mul i64 1000, 8
  %"alloc_call.2" = call i8* @"GC_malloc"(i64 %"alloc_size.2")
  %"i_load.3" = load i64, i64* %"i"
  %".17" = getelementptr i8, i8* %"alloc_call.2", i64 %"i_load.3"
  %"ptr_idx_load.2" = load i8, i8* %".17"
  %"idx_sext.2" = sext i8 %"ptr_idx_load.2" to i64
  %".18" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %".19" = bitcast [4 x i8]* @"str_10" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".19", i64 %"idx_sext.2")
  %".20" = bitcast [2 x i8]* @"str_11" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %"i_load.4" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.4", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
while_end:
  ret void
}

define void @"select_where_age_gt"(i64 %".1")
{
select_where_age_gt_entry:
  %"val" = alloca i64
  store i64 %".1", i64* %"val"
  br label %"select_where_age_gt_body"
select_where_age_gt_body:
  %".5" = bitcast [28 x i8]* @"str_12" to i8*
  %".6" = bitcast [3 x i8]* @"str_13" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".6", i8* %".5")
  %"val_load" = load i64, i64* %"val"
  %".7" = bitcast [2 x i8]* @"str_14" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".7")
  %".8" = bitcast [4 x i8]* @"str_15" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".8", i64 %"val_load")
  %".9" = bitcast [2 x i8]* @"str_16" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  %".10" = bitcast [19 x i8]* @"str_17" to i8*
  %".11" = bitcast [3 x i8]* @"str_18" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".10")
  %".12" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"g_row_count_load" = load i64, i64* @"g_row_count"
  %"icmp" = icmp slt i64 %"i_load", %"g_row_count_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"alloc_size" = mul i64 1000, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"i_load.1" = load i64, i64* %"i"
  %".16" = getelementptr i8, i8* %"alloc_call", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".16"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"val_load.1" = load i64, i64* %"val"
  %"icmp.1" = icmp sgt i64 %"idx_sext", %"val_load.1"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  ret void
if_then:
  %"alloc_size.1" = mul i64 1000, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"i_load.2" = load i64, i64* %"i"
  %".18" = getelementptr i8, i8* %"alloc_call.1", i64 %"i_load.2"
  %"ptr_idx_load.1" = load i8, i8* %".18"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %".19" = bitcast [4 x i8]* @"str_20" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".19", i64 %"idx_sext.1")
  %"alloc_size.2" = mul i64 1000, 8
  %"alloc_call.2" = call i8* @"GC_malloc"(i64 %"alloc_size.2")
  %"i_load.3" = load i64, i64* %"i"
  %".20" = getelementptr i8, i8* %"alloc_call.2", i64 %"i_load.3"
  %"ptr_idx_load.2" = load i8, i8* %".20"
  %"idx_sext.2" = sext i8 %"ptr_idx_load.2" to i64
  %".21" = bitcast [2 x i8]* @"str_21" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".21")
  %".22" = bitcast [4 x i8]* @"str_22" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".22", i64 %"idx_sext.2")
  %"alloc_size.3" = mul i64 1000, 8
  %"alloc_call.3" = call i8* @"GC_malloc"(i64 %"alloc_size.3")
  %"i_load.4" = load i64, i64* %"i"
  %".23" = getelementptr i8, i8* %"alloc_call.3", i64 %"i_load.4"
  %"ptr_idx_load.3" = load i8, i8* %".23"
  %"idx_sext.3" = sext i8 %"ptr_idx_load.3" to i64
  %".24" = bitcast [2 x i8]* @"str_23" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".24")
  %".25" = bitcast [4 x i8]* @"str_24" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".25", i64 %"idx_sext.3")
  %".26" = bitcast [2 x i8]* @"str_25" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".26")
  br label %"if_end"
if_else:
  br label %"if_end"
if_end:
  %"i_load.5" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.5", 1
  store i64 %"add", i64* %"i"
  br label %"while_cond"
}

define i64 @"sum_salary"()
{
sum_salary_entry:
  br label %"sum_salary_body"
sum_salary_body:
  %"total" = alloca i64
  store i64 0, i64* %"total"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"g_row_count_load" = load i64, i64* @"g_row_count"
  %"icmp" = icmp slt i64 %"i_load", %"g_row_count_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"total_load" = load i64, i64* %"total"
  %"alloc_size" = mul i64 1000, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"i_load.1" = load i64, i64* %"i"
  %".7" = getelementptr i8, i8* %"alloc_call", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".7"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"add" = add i64 %"total_load", %"idx_sext"
  store i64 %"add", i64* %"total"
  %"i_load.2" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.2", 1
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  %"total_load.1" = load i64, i64* %"total"
  ret i64 %"total_load.1"
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [44 x i8]* @"str_26" to i8*
  %".8" = bitcast [3 x i8]* @"str_27" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_28" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  call void @"insert"(i64 1, i64 25, i64 5000)
  call void @"insert"(i64 2, i64 35, i64 8000)
  call void @"insert"(i64 3, i64 42, i64 12000)
  call void @"insert"(i64 4, i64 28, i64 6000)
  call void @"insert"(i64 5, i64 31, i64 9000)
  %".10" = bitcast [21 x i8]* @"str_29" to i8*
  %".11" = bitcast [3 x i8]* @"str_30" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".11", i8* %".10")
  %"g_row_count_load" = load i64, i64* @"g_row_count"
  %".12" = bitcast [2 x i8]* @"str_31" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".12")
  %".13" = bitcast [4 x i8]* @"str_32" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".13", i64 %"g_row_count_load")
  %".14" = bitcast [2 x i8]* @"str_33" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".14")
  %".15" = bitcast [1 x i8]* @"str_34" to i8*
  %".16" = bitcast [3 x i8]* @"str_35" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".16", i8* %".15")
  %".17" = bitcast [2 x i8]* @"str_36" to i8*
  %"print_nl.2" = call i32 (i8*, ...) @"printf"(i8* %".17")
  %".18" = bitcast [32 x i8]* @"str_37" to i8*
  %".19" = bitcast [3 x i8]* @"str_38" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".19", i8* %".18")
  %".20" = bitcast [2 x i8]* @"str_39" to i8*
  %"print_nl.3" = call i32 (i8*, ...) @"printf"(i8* %".20")
  call void @"select_all"()
  %".21" = bitcast [1 x i8]* @"str_40" to i8*
  %".22" = bitcast [3 x i8]* @"str_41" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".22", i8* %".21")
  %".23" = bitcast [2 x i8]* @"str_42" to i8*
  %"print_nl.4" = call i32 (i8*, ...) @"printf"(i8* %".23")
  call void @"select_where_age_gt"(i64 30)
  %".24" = bitcast [1 x i8]* @"str_43" to i8*
  %".25" = bitcast [3 x i8]* @"str_44" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".25", i8* %".24")
  %".26" = bitcast [2 x i8]* @"str_45" to i8*
  %"print_nl.5" = call i32 (i8*, ...) @"printf"(i8* %".26")
  %"sum_salary_call" = call i64 @"sum_salary"()
  %"total_salaries" = alloca i64
  store i64 %"sum_salary_call", i64* %"total_salaries"
  %".28" = bitcast [42 x i8]* @"str_46" to i8*
  %".29" = bitcast [3 x i8]* @"str_47" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".29", i8* %".28")
  %".30" = bitcast [2 x i8]* @"str_48" to i8*
  %"print_nl.6" = call i32 (i8*, ...) @"printf"(i8* %".30")
  %".31" = bitcast [20 x i8]* @"str_49" to i8*
  %".32" = bitcast [3 x i8]* @"str_50" to i8*
  %"print_call.8" = call i32 (i8*, ...) @"printf"(i8* %".32", i8* %".31")
  %"total_salaries_load" = load i64, i64* %"total_salaries"
  %".33" = bitcast [2 x i8]* @"str_51" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".33")
  %".34" = bitcast [4 x i8]* @"str_52" to i8*
  %"print_call.9" = call i32 (i8*, ...) @"printf"(i8* %".34", i64 %"total_salaries_load")
  %".35" = bitcast [2 x i8]* @"str_53" to i8*
  %"print_nl.7" = call i32 (i8*, ...) @"printf"(i8* %".35")
  %"ret_trunc" = trunc i64 0 to i32
  ret i32 %"ret_trunc"
}

@"__lumina_argc" = global i32 0
@"__lumina_argv" = global i8** null
@"str_0" = constant [18 x i8] c"ID | Age | Salary\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c"\0a\00"
@"str_3" = constant [19 x i8] c"------------------\00"
@"str_4" = constant [3 x i8] c"%s\00"
@"str_5" = constant [2 x i8] c"\0a\00"
@"str_6" = constant [4 x i8] c"%ld\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c" \00"
@"str_10" = constant [4 x i8] c"%ld\00"
@"str_11" = constant [2 x i8] c"\0a\00"
@"str_12" = constant [28 x i8] c"Query: SELECT * WHERE age >\00"
@"str_13" = constant [3 x i8] c"%s\00"
@"str_14" = constant [2 x i8] c" \00"
@"str_15" = constant [4 x i8] c"%ld\00"
@"str_16" = constant [2 x i8] c"\0a\00"
@"str_17" = constant [19 x i8] c"------------------\00"
@"str_18" = constant [3 x i8] c"%s\00"
@"str_19" = constant [2 x i8] c"\0a\00"
@"str_20" = constant [4 x i8] c"%ld\00"
@"str_21" = constant [2 x i8] c" \00"
@"str_22" = constant [4 x i8] c"%ld\00"
@"str_23" = constant [2 x i8] c" \00"
@"str_24" = constant [4 x i8] c"%ld\00"
@"str_25" = constant [2 x i8] c"\0a\00"
@"str_26" = constant [44 x i8] c"\f0\9f\8f\97\ef\b8\8f  Iniciando Mini SQL Query Engine...\00"
@"str_27" = constant [3 x i8] c"%s\00"
@"str_28" = constant [2 x i8] c"\0a\00"
@"str_29" = constant [21 x i8] c"Registros inseridos:\00"
@"str_30" = constant [3 x i8] c"%s\00"
@"str_31" = constant [2 x i8] c" \00"
@"str_32" = constant [4 x i8] c"%ld\00"
@"str_33" = constant [2 x i8] c"\0a\00"
@"str_34" = constant [1 x i8] c"\00"
@"str_35" = constant [3 x i8] c"%s\00"
@"str_36" = constant [2 x i8] c"\0a\00"
@"str_37" = constant [32 x i8] c"Executando: SELECT * FROM table\00"
@"str_38" = constant [3 x i8] c"%s\00"
@"str_39" = constant [2 x i8] c"\0a\00"
@"str_40" = constant [1 x i8] c"\00"
@"str_41" = constant [3 x i8] c"%s\00"
@"str_42" = constant [2 x i8] c"\0a\00"
@"str_43" = constant [1 x i8] c"\00"
@"str_44" = constant [3 x i8] c"%s\00"
@"str_45" = constant [2 x i8] c"\0a\00"
@"str_46" = constant [42 x i8] c"Executando: SELECT SUM(salary) FROM table\00"
@"str_47" = constant [3 x i8] c"%s\00"
@"str_48" = constant [2 x i8] c"\0a\00"
@"str_49" = constant [20 x i8] c"Total de sal\c3\a1rios:\00"
@"str_50" = constant [3 x i8] c"%s\00"
@"str_51" = constant [2 x i8] c" \00"
@"str_52" = constant [4 x i8] c"%ld\00"
@"str_53" = constant [2 x i8] c"\0a\00"