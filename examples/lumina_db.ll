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
@"g_db_len" = internal global i64 0
define void @"put"(i64 %".1", i64 %".2")
{
put_entry:
  %"key" = alloca i64
  store i64 %".1", i64* %"key"
  %"val" = alloca i64
  store i64 %".2", i64* %"val"
  br label %"put_body"
put_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"g_db_len_load" = load i64, i64* @"g_db_len"
  %"icmp" = icmp slt i64 %"i_load", %"g_db_len_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"alloc_size" = mul i64 200, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"i_load.1" = load i64, i64* %"i"
  %".10" = getelementptr i8, i8* %"alloc_call", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".10"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"key_load" = load i64, i64* %"key"
  %"icmp.1" = icmp eq i64 %"idx_sext", %"key_load"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"key_load.2" = load i64, i64* %"key"
  %"alloc_size.2" = mul i64 200, 8
  %"alloc_call.2" = call i8* @"GC_malloc"(i64 %"alloc_size.2")
  %"g_db_len_load.1" = load i64, i64* @"g_db_len"
  %"idx_ptr.1" = getelementptr i8, i8* %"alloc_call.2", i64 %"g_db_len_load.1"
  %"elem_trunc.1" = trunc i64 %"key_load.2" to i8
  store i8 %"elem_trunc.1", i8* %"idx_ptr.1"
  %"val_load.2" = load i64, i64* %"val"
  %"alloc_size.3" = mul i64 200, 8
  %"alloc_call.3" = call i8* @"GC_malloc"(i64 %"alloc_size.3")
  %"g_db_len_load.2" = load i64, i64* @"g_db_len"
  %"add.2" = add i64 %"g_db_len_load.2", 1
  %"idx_ptr.2" = getelementptr i8, i8* %"alloc_call.3", i64 %"add.2"
  %"elem_trunc.2" = trunc i64 %"val_load.2" to i8
  store i8 %"elem_trunc.2", i8* %"idx_ptr.2"
  %"g_db_len_load.3" = load i64, i64* @"g_db_len"
  %"add.3" = add i64 %"g_db_len_load.3", 2
  store i64 %"add.3", i64* @"g_db_len"
  %".30" = bitcast [10 x i8]* @"str_10" to i8*
  %".31" = bitcast [3 x i8]* @"str_11" to i8*
  %"print_call.4" = call i32 (i8*, ...) @"printf"(i8* %".31", i8* %".30")
  %"key_load.3" = load i64, i64* %"key"
  %".32" = bitcast [2 x i8]* @"str_12" to i8*
  %"print_sep.3" = call i32 (i8*, ...) @"printf"(i8* %".32")
  %".33" = bitcast [4 x i8]* @"str_13" to i8*
  %"print_call.5" = call i32 (i8*, ...) @"printf"(i8* %".33", i64 %"key_load.3")
  %".34" = bitcast [3 x i8]* @"str_14" to i8*
  %".35" = bitcast [2 x i8]* @"str_15" to i8*
  %"print_sep.4" = call i32 (i8*, ...) @"printf"(i8* %".35")
  %".36" = bitcast [3 x i8]* @"str_16" to i8*
  %"print_call.6" = call i32 (i8*, ...) @"printf"(i8* %".36", i8* %".34")
  %"val_load.3" = load i64, i64* %"val"
  %".37" = bitcast [2 x i8]* @"str_17" to i8*
  %"print_sep.5" = call i32 (i8*, ...) @"printf"(i8* %".37")
  %".38" = bitcast [4 x i8]* @"str_18" to i8*
  %"print_call.7" = call i32 (i8*, ...) @"printf"(i8* %".38", i64 %"val_load.3")
  %".39" = bitcast [2 x i8]* @"str_19" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".39")
  ret void
if_then:
  %"val_load" = load i64, i64* %"val"
  %"alloc_size.1" = mul i64 200, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %"idx_ptr" = getelementptr i8, i8* %"alloc_call.1", i64 %"add"
  %"elem_trunc" = trunc i64 %"val_load" to i8
  store i8 %"elem_trunc", i8* %"idx_ptr"
  %".13" = bitcast [12 x i8]* @"str_0" to i8*
  %".14" = bitcast [3 x i8]* @"str_1" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".14", i8* %".13")
  %"key_load.1" = load i64, i64* %"key"
  %".15" = bitcast [2 x i8]* @"str_2" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".15")
  %".16" = bitcast [4 x i8]* @"str_3" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".16", i64 %"key_load.1")
  %".17" = bitcast [3 x i8]* @"str_4" to i8*
  %".18" = bitcast [2 x i8]* @"str_5" to i8*
  %"print_sep.1" = call i32 (i8*, ...) @"printf"(i8* %".18")
  %".19" = bitcast [3 x i8]* @"str_6" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".19", i8* %".17")
  %"val_load.1" = load i64, i64* %"val"
  %".20" = bitcast [2 x i8]* @"str_7" to i8*
  %"print_sep.2" = call i32 (i8*, ...) @"printf"(i8* %".20")
  %".21" = bitcast [4 x i8]* @"str_8" to i8*
  %"print_call.3" = call i32 (i8*, ...) @"printf"(i8* %".21", i64 %"val_load.1")
  %".22" = bitcast [2 x i8]* @"str_9" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".22")
  ret void
if_else:
  br label %"if_end"
if_end:
  %"i_load.3" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.3", 2
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
}

define i64 @"get"(i64 %".1")
{
get_entry:
  %"key" = alloca i64
  store i64 %".1", i64* %"key"
  br label %"get_body"
get_body:
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"g_db_len_load" = load i64, i64* @"g_db_len"
  %"icmp" = icmp slt i64 %"i_load", %"g_db_len_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"alloc_size" = mul i64 200, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"i_load.1" = load i64, i64* %"i"
  %".8" = getelementptr i8, i8* %"alloc_call", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".8"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %"key_load" = load i64, i64* %"key"
  %"icmp.1" = icmp eq i64 %"idx_sext", %"key_load"
  br i1 %"icmp.1", label %"if_then", label %"if_else"
while_end:
  %"neg" = sub i64 0, 1
  ret i64 %"neg"
if_then:
  %"alloc_size.1" = mul i64 200, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %".10" = getelementptr i8, i8* %"alloc_call.1", i64 %"add"
  %"ptr_idx_load.1" = load i8, i8* %".10"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  ret i64 %"idx_sext.1"
if_else:
  br label %"if_end"
if_end:
  %"i_load.3" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.3", 2
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
}

define void @"save"()
{
save_entry:
  br label %"save_body"
save_body:
  %".3" = bitcast [1 x i8]* @"str_20" to i8*
  %"data" = alloca i8*
  store i8* %".3", i8** %"data"
  %"i" = alloca i64
  store i64 0, i64* %"i"
  br label %"while_cond"
while_cond:
  %"i_load" = load i64, i64* %"i"
  %"g_db_len_load" = load i64, i64* @"g_db_len"
  %"icmp" = icmp slt i64 %"i_load", %"g_db_len_load"
  br i1 %"icmp", label %"while_body", label %"while_end"
while_body:
  %"data_load" = load i8*, i8** %"data"
  %"alloc_size" = mul i64 200, 8
  %"alloc_call" = call i8* @"GC_malloc"(i64 %"alloc_size")
  %"i_load.1" = load i64, i64* %"i"
  %".8" = getelementptr i8, i8* %"alloc_call", i64 %"i_load.1"
  %"ptr_idx_load" = load i8, i8* %".8"
  %"idx_sext" = sext i8 %"ptr_idx_load" to i64
  %".9" = bitcast [4 x i8]* @"str_21" to i8*
  %"num_to_str" = alloca [64 x i8]
  %"num_to_str_ptr" = bitcast [64 x i8]* %"num_to_str" to i8*
  %"num_to_str_call" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr", i64 64, i8* %".9", i64 %"idx_sext")
  %"sconcat_len1" = call i64 @"strlen"(i8* %"data_load")
  %"sconcat_len2" = call i64 @"strlen"(i8* %"num_to_str_ptr")
  %"sconcat_sum" = add i64 %"sconcat_len1", %"sconcat_len2"
  %"sconcat_total" = add i64 %"sconcat_sum", 1
  %"sconcat_buf" = call i8* @"GC_malloc"(i64 %"sconcat_total")
  %"sconcat_cpy" = call i8* @"strcpy"(i8* %"sconcat_buf", i8* %"data_load")
  %"sconcat_cat" = call i8* @"strcat"(i8* %"sconcat_buf", i8* %"num_to_str_ptr")
  %".10" = bitcast [2 x i8]* @"str_22" to i8*
  %"sconcat_len1.1" = call i64 @"strlen"(i8* %"sconcat_buf")
  %"sconcat_len2.1" = call i64 @"strlen"(i8* %".10")
  %"sconcat_sum.1" = add i64 %"sconcat_len1.1", %"sconcat_len2.1"
  %"sconcat_total.1" = add i64 %"sconcat_sum.1", 1
  %"sconcat_buf.1" = call i8* @"GC_malloc"(i64 %"sconcat_total.1")
  %"sconcat_cpy.1" = call i8* @"strcpy"(i8* %"sconcat_buf.1", i8* %"sconcat_buf")
  %"sconcat_cat.1" = call i8* @"strcat"(i8* %"sconcat_buf.1", i8* %".10")
  %"alloc_size.1" = mul i64 200, 8
  %"alloc_call.1" = call i8* @"GC_malloc"(i64 %"alloc_size.1")
  %"i_load.2" = load i64, i64* %"i"
  %"add" = add i64 %"i_load.2", 1
  %".11" = getelementptr i8, i8* %"alloc_call.1", i64 %"add"
  %"ptr_idx_load.1" = load i8, i8* %".11"
  %"idx_sext.1" = sext i8 %"ptr_idx_load.1" to i64
  %".12" = bitcast [4 x i8]* @"str_23" to i8*
  %"num_to_str.1" = alloca [64 x i8]
  %"num_to_str_ptr.1" = bitcast [64 x i8]* %"num_to_str.1" to i8*
  %"num_to_str_call.1" = call i32 (i8*, i64, i8*, ...) @"snprintf"(i8* %"num_to_str_ptr.1", i64 64, i8* %".12", i64 %"idx_sext.1")
  %"sconcat_len1.2" = call i64 @"strlen"(i8* %"sconcat_buf.1")
  %"sconcat_len2.2" = call i64 @"strlen"(i8* %"num_to_str_ptr.1")
  %"sconcat_sum.2" = add i64 %"sconcat_len1.2", %"sconcat_len2.2"
  %"sconcat_total.2" = add i64 %"sconcat_sum.2", 1
  %"sconcat_buf.2" = call i8* @"GC_malloc"(i64 %"sconcat_total.2")
  %"sconcat_cpy.2" = call i8* @"strcpy"(i8* %"sconcat_buf.2", i8* %"sconcat_buf.1")
  %"sconcat_cat.2" = call i8* @"strcat"(i8* %"sconcat_buf.2", i8* %"num_to_str_ptr.1")
  %".13" = bitcast [2 x i8]* @"str_24" to i8*
  %"sconcat_len1.3" = call i64 @"strlen"(i8* %"sconcat_buf.2")
  %"sconcat_len2.3" = call i64 @"strlen"(i8* %".13")
  %"sconcat_sum.3" = add i64 %"sconcat_len1.3", %"sconcat_len2.3"
  %"sconcat_total.3" = add i64 %"sconcat_sum.3", 1
  %"sconcat_buf.3" = call i8* @"GC_malloc"(i64 %"sconcat_total.3")
  %"sconcat_cpy.3" = call i8* @"strcpy"(i8* %"sconcat_buf.3", i8* %"sconcat_buf.2")
  %"sconcat_cat.3" = call i8* @"strcat"(i8* %"sconcat_buf.3", i8* %".13")
  store i8* %"sconcat_buf.3", i8** %"data"
  %"i_load.3" = load i64, i64* %"i"
  %"add.1" = add i64 %"i_load.3", 2
  store i64 %"add.1", i64* %"i"
  br label %"while_cond"
while_end:
  %".17" = bitcast [14 x i8]* @"str_25" to i8*
  %"data_load.1" = load i8*, i8** %"data"
  %".18" = bitcast [2 x i8]* @"str_26" to i8*
  %"wf_fopen" = call i8* @"fopen"(i8* %".17", i8* %".18")
  %"wf_fputs" = call i32 @"fputs"(i8* %"data_load.1", i8* %"wf_fopen")
  %"wf_fclose" = call i32 @"fclose"(i8* %"wf_fopen")
  %".19" = bitcast [44 x i8]* @"str_27" to i8*
  %".20" = bitcast [3 x i8]* @"str_28" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".20", i8* %".19")
  %".21" = bitcast [2 x i8]* @"str_29" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".21")
  ret void
}

define i32 @"main"(i32 %".1", i8** %".2")
{
main_entry:
  call void @"GC_init"()
  store i32 %".1", i32* @"__lumina_argc"
  store i8** %".2", i8*** @"__lumina_argv"
  br label %"main_body"
main_body:
  %".7" = bitcast [27 x i8]* @"str_30" to i8*
  %".8" = bitcast [3 x i8]* @"str_31" to i8*
  %"print_call" = call i32 (i8*, ...) @"printf"(i8* %".8", i8* %".7")
  %".9" = bitcast [2 x i8]* @"str_32" to i8*
  %"print_nl" = call i32 (i8*, ...) @"printf"(i8* %".9")
  call void @"put"(i64 1, i64 100)
  call void @"put"(i64 2, i64 200)
  call void @"put"(i64 3, i64 300)
  call void @"put"(i64 2, i64 999)
  %"get_call" = call i64 @"get"(i64 2)
  %"val" = alloca i64
  store i64 %"get_call", i64* %"val"
  %".11" = bitcast [15 x i8]* @"str_33" to i8*
  %".12" = bitcast [3 x i8]* @"str_34" to i8*
  %"print_call.1" = call i32 (i8*, ...) @"printf"(i8* %".12", i8* %".11")
  %"val_load" = load i64, i64* %"val"
  %".13" = bitcast [2 x i8]* @"str_35" to i8*
  %"print_sep" = call i32 (i8*, ...) @"printf"(i8* %".13")
  %".14" = bitcast [4 x i8]* @"str_36" to i8*
  %"print_call.2" = call i32 (i8*, ...) @"printf"(i8* %".14", i64 %"val_load")
  %".15" = bitcast [2 x i8]* @"str_37" to i8*
  %"print_nl.1" = call i32 (i8*, ...) @"printf"(i8* %".15")
  call void @"save"()
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

@"str_0" = constant [12 x i8] c"Atualizado:\00"
@"str_1" = constant [3 x i8] c"%s\00"
@"str_2" = constant [2 x i8] c" \00"
@"str_3" = constant [4 x i8] c"%ld\00"
@"str_4" = constant [3 x i8] c"->\00"
@"str_5" = constant [2 x i8] c" \00"
@"str_6" = constant [3 x i8] c"%s\00"
@"str_7" = constant [2 x i8] c" \00"
@"str_8" = constant [4 x i8] c"%ld\00"
@"str_9" = constant [2 x i8] c"\0a\00"
@"str_10" = constant [10 x i8] c"Inserido:\00"
@"str_11" = constant [3 x i8] c"%s\00"
@"str_12" = constant [2 x i8] c" \00"
@"str_13" = constant [4 x i8] c"%ld\00"
@"str_14" = constant [3 x i8] c"->\00"
@"str_15" = constant [2 x i8] c" \00"
@"str_16" = constant [3 x i8] c"%s\00"
@"str_17" = constant [2 x i8] c" \00"
@"str_18" = constant [4 x i8] c"%ld\00"
@"str_19" = constant [2 x i8] c"\0a\00"
@"str_20" = constant [1 x i8] c"\00"
@"str_21" = constant [4 x i8] c"%ld\00"
@"str_22" = constant [2 x i8] c",\00"
@"str_23" = constant [4 x i8] c"%ld\00"
@"str_24" = constant [2 x i8] c"\0a\00"
@"str_25" = constant [14 x i8] c"lumina_db.txt\00"
declare i8* @"fopen"(i8* %".1", i8* %".2")

declare i32 @"fputs"(i8* %".1", i8* %".2")

declare i32 @"fclose"(i8* %".1")

@"str_26" = constant [2 x i8] c"w\00"
@"str_27" = constant [44 x i8] c"\f0\9f\92\be Banco de dados salvo em lumina_db.txt!\00"
@"str_28" = constant [3 x i8] c"%s\00"
@"str_29" = constant [2 x i8] c"\0a\00"
@"str_30" = constant [27 x i8] c"\f0\9f\9a\80 LuminaDB iniciando...\00"
@"str_31" = constant [3 x i8] c"%s\00"
@"str_32" = constant [2 x i8] c"\0a\00"
@"str_33" = constant [15 x i8] c"Busca chave 2:\00"
@"str_34" = constant [3 x i8] c"%s\00"
@"str_35" = constant [2 x i8] c" \00"
@"str_36" = constant [4 x i8] c"%ld\00"
@"str_37" = constant [2 x i8] c"\0a\00"